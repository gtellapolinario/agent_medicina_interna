#!/usr/bin/env python3
"""
app_v3.py

Aplicação Streamlit profissional para demonstração de um agente de anamnese clínica
baseado em prompt + skill bundle.

Recursos principais:
- execução única
- comparação com skill vs sem skill
- comparação prompt enxuto vs prompt completo
- preview local sem API
- execução com OpenAI Responses API
- casos de teste prontos
- upload de transcrição
- inspeção do bundle da skill
- checklist automático de qualidade
- exportação em Markdown e JSON
- diagnóstico de integridade da pasta da skill

Uso:
    pip install streamlit openai
    export OPENAI_API_KEY="sua_chave"
    python create_skill_bundle.py
    streamlit run app_v3.py
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st

try:
    from openai import OpenAI
except Exception:
    OpenAI = None


APP_TITLE = "Tester v3 — Agente de Anamnese Clínica"
APP_SUBTITLE = "Demonstração profissional de prompt + skill bundle para análise de transcrição de consulta gravada"


PROMPT_ENXUTO = """# PROMPT FINAL — Agente de Anamnese em Clínica Médica com SOAP

## 1) Função
Aja como **Agente Clínico de Anamnese** especializado em **clínica médica / medicina interna / ambulatório**, capaz de analisar **transcrições de consultas gravadas** e convertê-las em **anamnese estruturada clinicamente útil**, com **hipóteses diagnósticas, red flags, limitações, sugestões de seguimento** e **fechamento em SOAP**.

## 2) Objetivo
Transformar uma **transcrição de áudio de consulta médica**, potencialmente imperfeita, incompleta e heterogênea, em uma síntese clínica estruturada, fiel ao conteúdo disponível.

## 3) Regras centrais
- **Não inventar dados**.
- Distinguir sempre entre:
  - **dado referido pelo paciente**,
  - **achado objetivo documentado**,
  - **inferência clínica plausível**.
- **Não presumir ausência clínica** só porque algo não foi mencionado.
- Quando a consulta não abordar um tópico periférico, **omitir** ou marcar como **[não explorado na transcrição]**.
- Quando faltar informação em parte essencial, manter a seção e registrar como **inferência clínica** ou **[informação não disponível]**.
- **Não afirmar** exame físico, sinais vitais, exames, diagnósticos confirmados ou condutas prévias se isso não constar.
- Se houver sinais de gravidade, destacar necessidade de **avaliação urgente/emergencial**.

## 4) Particularidades da transcrição gravada
A entrada pode conter:
- erros de ASR,
- troca de falantes,
- frases truncadas,
- omissões,
- ruído conversacional,
- termos médicos mal transcritos.

Antes de estruturar:
- normalize o texto minimamente;
- identifique, se possível, quem é paciente e quem é profissional;
- preserve ambiguidades reais;
- não corrija semanticamente com excesso de confiança;
- se um termo parecer erro de transcrição, sinalize como **[termo possivelmente mal transcrito]**;
- se houver dúvida sobre falante, registrar isso em **Limitações**.

## 5) Regra de heterogeneidade
Como se trata de consulta gravada, **nem toda saída precisa contemplar todos os blocos do template**.

Portanto:
- blocos **não essenciais** podem ser omitidos ou marcados como **[não explorado na transcrição]**;
- blocos **essenciais** devem sempre ser produzidos, mesmo que de forma sucinta:
  - **Impressão Clínica**
  - **Hipóteses Diagnósticas e Diferenciais**
  - **Red Flags**
  - **Limitações**
  - **SOAP FINAL**

## 6) Ferramentas e fontes
- Pode usar **web autorizada** quando isso aumentar materialmente a correção clínica.
- Se usar web:
  - priorizar diretrizes, consensos, revisões sistemáticas e documentos oficiais;
  - preferir fontes dos últimos 5 anos, admitindo clássicos indispensáveis;
  - citar até **5 fontes load-bearing** em **Vancouver curto**.

## 7) Formato de saída
Responder em **pt-BR**, em **Markdown**, com tom **clínico, técnico, objetivo e auditável**.

### A. Identificação
### B. Queixa principal (QP)
### C. História da Doença Atual (HDA)
### D. Revisão Dirigida de Sintomas (RDS / ROS)
### E. Antecedentes Pessoais
### F. Antecedentes Familiares
### G. Hábitos de Vida e Contexto Biopsicossocial
### H. Exame Físico e Dados Objetivos
### I. Síntese dos Dados por Natureza
### J. Impressão Clínica
### K. Hipóteses Diagnósticas e Diagnóstico Diferencial
### L. Red Flags / Sinais de Alarme
### M. Conduta e Plano Inicial
### N. Limitações
### O. SOAP FINAL
"""

PROMPT_COMPLETO = """# PROMPT FINAL — Agente de Anamnese em Clínica Médica com Síntese Estruturada e Fechamento em SOAP

## 1) Função
Aja como Agente Clínico de Anamnese especializado em clínica médica / medicina interna / atenção ambulatorial, com competência para analisar transcrições de consultas, extrair dados clínicos com rigor, organizar a informação semiologicamente e produzir uma síntese clínica estruturada, auditável e clinicamente útil, encerrando com SOAP final consistente.

## 2) Objetivo
Transformar uma transcrição de áudio de consulta de clínica médica, potencialmente imperfeita e heterogênea, em uma anamnese estruturada clinicamente útil, fiel ao conteúdo disponível, com hipóteses diagnósticas, avaliação de gravidade, lacunas relevantes, plano inicial e fechamento em SOAP.

## 3) Princípios obrigatórios
- Não inventar dados.
- Não transformar inferência em fato documentado.
- Distinguir sempre entre dado referido pelo paciente, achado objetivo documentado e inferência clínica plausível.
- Não presumir ausência clínica apenas porque algo não foi mencionado.
- Não forçar completude artificial em consulta gravada heterogênea.
- Manter obrigatoriamente os blocos essenciais: Impressão Clínica, Hipóteses Diagnósticas e Diagnóstico Diferencial, Red Flags / Sinais de Alarme, Limitações e SOAP FINAL.
- Quando a consulta não trouxer conduta explícita, podem ser incluídas sugestões prudentes de seguimento/investigação, rotuladas como sugestão clínica inferida.

## 4) Particularidades da transcrição gravada
Assuma que a entrada pode conter erros de ASR, pontuação imperfeita, troca de falantes, repetições, interrupções, omissões, ruído conversacional e termos médicos mal transcritos.

## 5) Regras de saída
Responder em pt-BR, em Markdown, com tom clínico, técnico, objetivo e auditável, contemplando:
A. Identificação
B. Queixa principal (QP)
C. História da Doença Atual (HDA)
D. Revisão Dirigida de Sintomas (RDS / ROS)
E. Antecedentes Pessoais
F. Antecedentes Familiares
G. Hábitos de Vida e Contexto Biopsicossocial
H. Exame Físico e Dados Objetivos
I. Síntese dos Dados por Natureza
J. Impressão Clínica
K. Hipóteses Diagnósticas e Diagnóstico Diferencial
L. Red Flags / Sinais de Alarme
M. Conduta e Plano Inicial
N. Limitações
O. SOAP FINAL
P. Referências, somente se houver uso de web

## 6) Segurança
Se houver sinais como dor torácica sugestiva, dispneia importante, sinais neurológicos focais, síncope, hemorragia importante, sepse, rebaixamento do nível de consciência, desidratação grave, abdome agudo, tromboembolismo ou risco suicida, destacar necessidade de avaliação urgente/emergencial.

## 7) Busca externa
Pode usar web autorizada para critérios diagnósticos, red flags e diretrizes. Se usar web, priorizar diretrizes, consensos, revisões sistemáticas e documentos oficiais. Citar até 5 fontes load-bearing.
"""

TEST_CASES = {
    "Dispneia com ortopneia e edema": """Profissional: O que está sentindo?
Paciente: Estou com falta de ar quando subo escadas há umas duas semanas.
Paciente: Nos últimos três dias piorou um pouco e tenho dormido com dois travesseiros.
Profissional: Febre? Dor no peito?
Paciente: Febre não. Dor no peito não exatamente, às vezes um aperto leve.
Paciente: Também notei inchaço nos tornozelos no fim do dia.
Profissional: Tem pressão alta ou diabetes?
Paciente: Tenho os dois. Tomo remédio, mas às vezes esqueço.
Profissional: Algum exame recente?
Paciente: Não, faz tempo que não faço.
""",
    "Dor abdominal com lacunas": """Profissional: O que trouxe você aqui?
Paciente: Estou com dor na barriga faz uns três dias.
Profissional: Onde dói mais?
Paciente: Mais do lado direito, embaixo, acho.
Profissional: Teve febre, vômito, diarreia?
Paciente: Vômito não. Febre eu não medi. Diarreia também não.
Paciente: Estou sem muito apetite.
Profissional: Já operou alguma vez?
Paciente: Não lembro de cirurgia, não.
""",
    "Cefaleia com transcrição imperfeita": """Profissional: Conta pra mim.
Paciente: Dor de cabeça... faz... acho que quatro dias.
Paciente: ontem piorô... luz incomoda... meio enjoo.
Profissional: Febre? visão?
Paciente: febre nao... visao meio embaça às vezes... ou acho que é do cansaço.
Profissional: fraqueza, fala enrolada?
Paciente: não... quer dizer... acho que não.
Paciente: tomei dipirona mas voltou.
""",
    "Seguimento multimorbidade": """Profissional: Como passou desde a última consulta?
Paciente: A glicose melhorou um pouco, mas continuo cansado.
Paciente: Minha pressão em casa às vezes fica alta.
Profissional: Está usando as medicações certinho?
Paciente: A maioria sim, mas esqueço a do almoço.
Profissional: E atividade física?
Paciente: Quase nada.
Profissional: Alguma dor no peito, falta de ar, inchaço?
Paciente: Dor no peito não. Falta de ar só quando ando rápido. Inchaço não.
""",
}

EXPECTED_SKILL_FILES = [
    Path("SKILL.md"),
    Path("README.md"),
    Path("references/red_flags_gerais.md"),
    Path("references/estrutura_soap.md"),
    Path("references/principios_grounding_clinico.md"),
    Path("assets/template_saida.md"),
]


@dataclass
class SkillBundleStatus:
    path: Path
    found_files: Dict[str, str]
    missing_files: List[str]

    @property
    def is_valid(self) -> bool:
        return len(self.found_files) > 0 and len(self.missing_files) == 0


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .main .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        .app-subtitle {color: #A0A7B4; margin-top: -0.5rem; margin-bottom: 1rem;}
        .metric-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            padding: 16px;
        }
        .section-caption {
            color: #8B93A7;
            font-size: 0.92rem;
            margin-bottom: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def inspect_skill_bundle(skill_dir: Path) -> SkillBundleStatus:
    found: Dict[str, str] = {}
    missing: List[str] = []
    if not skill_dir.exists():
        return SkillBundleStatus(path=skill_dir, found_files={}, missing_files=[str(p) for p in EXPECTED_SKILL_FILES])

    for rel in EXPECTED_SKILL_FILES:
        full = skill_dir / rel
        if full.exists():
            found[str(rel)] = read_text(full)
        else:
            missing.append(str(rel))
    return SkillBundleStatus(path=skill_dir, found_files=found, missing_files=missing)


def compose_system_prompt(base_prompt: str, skill_content: Dict[str, str], use_skill: bool) -> str:
    if not use_skill or not skill_content:
        return base_prompt.strip()

    parts: List[str] = [base_prompt.strip(), "\n\n# SKILL BUNDLE CARREGADA\n"]
    for name, content in skill_content.items():
        parts.append(f"\n## Arquivo: {name}\n{content.strip()}\n")
    return "\n".join(parts).strip()


def build_user_message(transcript: str, output_format: str) -> str:
    return f"""Analise a transcrição clínica abaixo e produza a saída final no formato solicitado.

Formato desejado: {output_format}

Transcrição:
\"\"\"
{transcript.strip()}
\"\"\"
""".strip()


def evaluate_output(text: str) -> Dict[str, bool]:
    lowered = text.lower()
    return {
        "impressao_clinica": "impressão clínica" in lowered or "impressao clinica" in lowered,
        "hipoteses": "hipóteses" in lowered or "hipoteses" in lowered,
        "red_flags": "red flags" in lowered or "sinais de alarme" in lowered,
        "limitacoes": "limitações" in lowered or "limitacoes" in lowered,
        "soap": "soap" in lowered or all(k in lowered for k in ["subjective", "objective", "assessment", "plan"]),
        "marcacao_ausencias": any(
            x in lowered
            for x in [
                "[não explorado na transcrição]",
                "[nao explorado na transcrição]",
                "[não documentado na transcrição]",
                "[nao documentado na transcrição]",
                "[informação não disponível]",
                "[informacao nao disponivel]",
            ]
        ),
    }


def render_checklist(checks: Dict[str, bool]) -> None:
    labels = {
        "impressao_clinica": "Impressão Clínica",
        "hipoteses": "Hipóteses diagnósticas",
        "red_flags": "Red flags",
        "limitacoes": "Limitações",
        "soap": "SOAP final",
        "marcacao_ausencias": "Marcação de ausências/lacunas",
    }
    for key, value in checks.items():
        st.write(("✅ " if value else "⚠️ ") + labels[key])


def sanitize_filename(name: str) -> str:
    return (re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip()) or "resultado")[:80]


def export_json(output: str, checks: Dict[str, bool], metadata: Dict[str, str]) -> str:
    payload = {
        "metadata": metadata,
        "checks": checks,
        "output": output,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def call_openai_responses(model: str, system_prompt: str, user_message: str, temperature: float) -> str:
    if OpenAI is None:
        raise RuntimeError("Pacote 'openai' não instalado. Rode: pip install openai")
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("Variável OPENAI_API_KEY não definida.")
    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_message}]},
        ],
        temperature=temperature,
    )
    return getattr(response, "output_text", "") or ""


def preview_result() -> str:
    return """# Preview de execução

## Impressão Clínica
Esperada.

## Hipóteses Diagnósticas e Diagnóstico Diferencial
Esperadas.

## Red Flags / Sinais de Alarme
Esperados.

## Limitações
Esperadas.

## SOAP FINAL
**S — Subjective**
**O — Objective**
**A — Assessment**
**P — Plan**
"""


def run_model(mode: str, model: str, system_prompt: str, user_message: str, temperature: float) -> str:
    if mode == "Preview local":
        return preview_result()
    return call_openai_responses(model, system_prompt, user_message, temperature)


def result_block(title: str, output: str, output_format: str, checks: Dict[str, bool], metadata: Dict[str, str]) -> None:
    st.subheader(title)

    result_tab, checks_tab, export_tab = st.tabs(["Resultado", "Checklist", "Exportar"])

    with result_tab:
        if output_format == "JSON":
            try:
                st.json(json.loads(output))
            except Exception:
                st.code(output, language="json")
        else:
            st.markdown(output)

    with checks_tab:
        render_checklist(checks)

    with export_tab:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = sanitize_filename(title)
        st.download_button(
            "Baixar Markdown",
            data=output,
            file_name=f"{base}_{stamp}.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.download_button(
            "Baixar JSON",
            data=export_json(output, checks, metadata),
            file_name=f"{base}_{stamp}.json",
            mime="application/json",
            use_container_width=True,
        )


def sidebar_controls() -> Dict[str, object]:
    st.sidebar.header("Configuração")

    mode = st.sidebar.radio(
        "Modo de execução",
        ["Preview local", "Executar com OpenAI API"],
        index=0,
    )

    test_mode = st.sidebar.selectbox(
        "Modo de teste",
        [
            "Execução única",
            "Comparar com skill vs sem skill",
            "Comparar prompt enxuto vs completo",
        ],
        index=0,
    )

    prompt_kind = st.sidebar.selectbox(
        "Prompt base",
        ["Enxuto", "Completo"],
        index=0,
    )

    use_skill = st.sidebar.checkbox("Usar skill bundle", value=True)

    default_skill_dir = Path.cwd() / "anamnese-clinica-consulta-gravada"
    skill_dir = st.sidebar.text_input("Pasta da skill", value=str(default_skill_dir))

    output_format = st.sidebar.selectbox("Formato de saída desejado", ["Markdown", "JSON"], index=0)
    model = st.sidebar.text_input("Modelo", value="gpt-5.4")
    temperature = st.sidebar.slider("Temperatura", 0.0, 1.0, 0.2, 0.1)

    return {
        "mode": mode,
        "test_mode": test_mode,
        "prompt_kind": prompt_kind,
        "use_skill": use_skill,
        "skill_dir": skill_dir,
        "output_format": output_format,
        "model": model,
        "temperature": temperature,
    }


def overview_metrics(transcript: str, skill_status: SkillBundleStatus, use_skill: bool) -> None:
    words = len(transcript.split()) if transcript.strip() else 0
    cols = st.columns(4)
    cols[0].metric("Palavras na transcrição", words)
    cols[1].metric("Arquivos da skill", len(skill_status.found_files))
    cols[2].metric("Arquivos ausentes", len(skill_status.missing_files))
    cols[3].metric("Skill ativa", "Sim" if use_skill else "Não")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    inject_css()

    st.title(APP_TITLE)
    st.markdown(f"<div class='app-subtitle'>{APP_SUBTITLE}</div>", unsafe_allow_html=True)

    config = sidebar_controls()

    selected_prompt = PROMPT_ENXUTO if config["prompt_kind"] == "Enxuto" else PROMPT_COMPLETO
    default_transcript = ""
    case_name = st.sidebar.selectbox("Caso de teste", ["Manual"] + list(TEST_CASES.keys()), index=0)
    if case_name != "Manual":
        default_transcript = TEST_CASES[case_name]

    left, right = st.columns([1.1, 0.9])

    with left:
        st.subheader("Entrada")
        uploaded = st.file_uploader("Enviar transcrição (.txt, .md)", type=["txt", "md"])
        transcript = default_transcript
        if uploaded is not None:
            transcript = uploaded.read().decode("utf-8", errors="replace")

        transcript = st.text_area("Transcrição clínica", value=transcript, height=320)

        st.subheader("Prompt")
        base_prompt = st.text_area("Prompt configurável", value=selected_prompt, height=430)

    skill_status = inspect_skill_bundle(Path(str(config["skill_dir"])).expanduser())
    composed_prompt = compose_system_prompt(base_prompt, skill_status.found_files, bool(config["use_skill"]))
    user_message = build_user_message(transcript, str(config["output_format"]))

    with right:
        st.subheader("Painel de contexto")
        overview_metrics(transcript, skill_status, bool(config["use_skill"]))

        status_tab, prompt_tab, skill_tab = st.tabs(["Status", "Prompt final", "Skill bundle"])

        with status_tab:
            if config["use_skill"]:
                if skill_status.found_files:
                    st.success(f"Skill localizada em: {skill_status.path}")
                    if skill_status.missing_files:
                        st.warning("A skill foi localizada, mas há arquivos ausentes.")
                    else:
                        st.info("Integridade da skill bundle: completa.")
                else:
                    st.warning("Nenhum arquivo da skill foi encontrado na pasta informada.")
            else:
                st.info("Skill bundle desativada nesta execução.")

            if skill_status.missing_files:
                st.markdown("**Arquivos ausentes**")
                for item in skill_status.missing_files:
                    st.write(f"- {item}")

        with prompt_tab:
            st.code(composed_prompt[:15000], language="markdown")
            with st.expander("Mensagem do usuário"):
                st.code(user_message, language="markdown")

        with skill_tab:
            if skill_status.found_files:
                for name, content in skill_status.found_files.items():
                    with st.expander(name):
                        st.code(content[:5000], language="markdown")
            else:
                st.caption("Nenhum arquivo encontrado.")

    st.divider()

    actions_col1, actions_col2 = st.columns([0.7, 0.3])
    with actions_col1:
        st.markdown("### Execução")
        st.caption("Execute em modo local para validar a composição ou chame a API para testar o comportamento real do agente.")
    with actions_col2:
        run = st.button("Executar teste", type="primary", use_container_width=True)

    if not run:
        return

    if not transcript.strip():
        st.error("Forneça uma transcrição antes de executar.")
        return

    if config["test_mode"] == "Execução única":
        try:
            with st.spinner("Executando..."):
                output = run_model(
                    str(config["mode"]),
                    str(config["model"]),
                    composed_prompt,
                    user_message,
                    float(config["temperature"]),
                )
            checks = evaluate_output(output)
            metadata = {
                "modo_execucao": str(config["mode"]),
                "modo_teste": str(config["test_mode"]),
                "prompt": str(config["prompt_kind"]),
                "skill_ativa": str(config["use_skill"]),
                "formato": str(config["output_format"]),
                "modelo": str(config["model"]),
                "caso": case_name,
            }
            result_block("Resultado da execução", output, str(config["output_format"]), checks, metadata)
        except Exception as exc:
            st.error(str(exc))
        return

    if config["test_mode"] == "Comparar com skill vs sem skill":
        compare_configs: List[Tuple[str, str]] = [
            ("Sem skill", compose_system_prompt(base_prompt, skill_status.found_files, False)),
            ("Com skill", compose_system_prompt(base_prompt, skill_status.found_files, True)),
        ]
    else:
        compare_configs = [
            ("Prompt enxuto", compose_system_prompt(PROMPT_ENXUTO, skill_status.found_files, bool(config["use_skill"]))),
            ("Prompt completo", compose_system_prompt(PROMPT_COMPLETO, skill_status.found_files, bool(config["use_skill"]))),
        ]

    col_a, col_b = st.columns(2)
    for container, (title, system_prompt) in zip([col_a, col_b], compare_configs):
        with container:
            try:
                with st.spinner(f"Executando: {title}"):
                    output = run_model(
                        str(config["mode"]),
                        str(config["model"]),
                        system_prompt,
                        user_message,
                        float(config["temperature"]),
                    )
                checks = evaluate_output(output)
                metadata = {
                    "modo_execucao": str(config["mode"]),
                    "modo_teste": str(config["test_mode"]),
                    "cenario": title,
                    "skill_ativa": str(config["use_skill"]),
                    "formato": str(config["output_format"]),
                    "modelo": str(config["model"]),
                    "caso": case_name,
                }
                result_block(title, output, str(config["output_format"]), checks, metadata)
            except Exception as exc:
                st.error(f"{title}: {exc}")

    with st.expander("Como rodar localmente"):
        st.code(
            "pip install streamlit openai\n"
            "export OPENAI_API_KEY='sua_chave'\n"
            "python create_skill_bundle.py\n"
            "streamlit run app_v3.py",
            language="bash",
        )


if __name__ == "__main__":
    main()
