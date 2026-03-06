---
name: anamnese-clinica-consulta-gravada
description: Use esta skill quando a tarefa for analisar transcrição de áudio de consulta de clínica médica/medicina interna/ambulatório e produzir anamnese estruturada, hipóteses diagnósticas, red flags, limitações, sugestões de seguimento e fechamento em SOAP, mesmo quando a transcrição estiver incompleta, heterogênea ou com erros de ASR.
---

# Anamnese Clínica de Consulta Gravada

## Quando usar
Use esta skill quando o usuário pedir para:

- analisar uma **transcrição de consulta médica**;
- converter uma **consulta gravada/transcrita** em **anamnese estruturada**;
- gerar **síntese clínica**, **hipóteses diagnósticas**, **diferenciais**, **red flags** ou **SOAP** a partir de conversa clínica;
- estruturar atendimento de **clínica médica / medicina interna / ambulatório** com base em transcrição textual;
- organizar consulta com saída em **Markdown** ou **JSON**.

Não use esta skill para:

- interpretar **áudio bruto** sem transcrição;
- fornecer diagnóstico definitivo sem base suficiente;
- substituir avaliação médica presencial em casos de urgência/emergência;
- inventar exame físico, sinais vitais, exames complementares ou condutas não documentadas.

## Objetivo
Transformar uma **transcrição de áudio de consulta de clínica médica**, potencialmente imperfeita e heterogênea, em uma **anamnese estruturada clinicamente útil**, fiel ao conteúdo disponível, com:

- organização semiológica;
- distinção entre relato, dado objetivo e inferência;
- hipóteses diagnósticas e diferenciais;
- avaliação de gravidade;
- red flags;
- limitações;
- sugestões prudentes de seguimento;
- fechamento em **SOAP**.

## Princípios obrigatórios
1. **Não inventar dados.**
2. **Não transformar inferência em fato documentado.**
3. **Distinguir sempre**:
   - dado referido pelo paciente;
   - achado objetivo documentado;
   - inferência clínica plausível.
4. **Não presumir ausência clínica** apenas porque algo não foi mencionado.
5. **Não forçar completude artificial** em consulta gravada heterogênea.
6. **Manter obrigatoriamente os blocos essenciais**:
   - Impressão Clínica;
   - Hipóteses Diagnósticas e Diagnóstico Diferencial;
   - Red Flags / Sinais de Alarme;
   - Limitações;
   - SOAP FINAL.
7. Quando a consulta não trouxer conduta explícita, podem ser incluídas **sugestões prudentes de seguimento/investigação**, mas elas devem ser apresentadas como **sugestão clínica inferida**, e não como conduta já definida pelo profissional assistente.

## Natureza da entrada
Assuma que a entrada é uma **transcrição de consulta gravada** e pode conter:

- erros de reconhecimento automático de fala (ASR);
- pontuação imperfeita;
- troca de falantes;
- repetições, interrupções e frases truncadas;
- omissões;
- ruído conversacional;
- termos médicos mal transcritos;
- consultas muito diferentes entre si, com cobertura desigual dos tópicos.

## Como lidar com transcrição imperfeita
Antes de estruturar a anamnese:

1. normalize o texto minimamente;
2. identifique, quando possível, quem é paciente e quem é profissional;
3. preserve ambiguidades reais;
4. não “corrija” semanticamente com excesso de confiança;
5. quando um termo parecer erro de transcrição, sinalize como **[termo possivelmente mal transcrito]** ou trate sua interpretação apenas como **inferência clínica plausível**;
6. se a atribuição do falante for incerta, registre isso em **Limitações**.

## Regra de heterogeneidade
Como se trata de consulta gravada:

- as saídas **não precisam ser idênticas** entre casos;
- nem toda consulta contemplará todos os domínios do template;
- blocos não essenciais podem ser:
  - omitidos, se sua ausência não comprometer a utilidade clínica; ou
  - marcados como **[não explorado na transcrição]**;
- blocos essenciais devem sempre ser produzidos, ainda que de forma sucinta.

## Fluxo de execução
Siga esta sequência:

1. Ler a transcrição como consulta gravada potencialmente imperfeita.
2. Extrair apenas os dados explícitos.
3. Separar conteúdo em:
   - relato do paciente;
   - dado objetivo documentado;
   - inferência clínica.
4. Organizar a anamnese por eixos clínicos e semiológicos.
5. Preencher apenas o que a consulta realmente contempla.
6. Produzir obrigatoriamente os componentes essenciais.
7. Avaliar gravidade e red flags.
8. Formular hipóteses diagnósticas e diferenciais.
9. Registrar limitações e lacunas.
10. Encerrar com SOAP final coerente.

## Regras de grounding
Toda afirmação deve cair em uma destas categorias:

- **Relato do paciente**: sintomas, percepções, negações, cronologia e contexto referidos.
- **Achado objetivo documentado**: sinais vitais, exame físico, exames laboratoriais, imagem, escalas e outras medidas explicitamente presentes na transcrição.
- **Inferência clínica plausível**: síntese técnica do modelo baseada nos dados disponíveis.

Nunca misture essas categorias.

## Regras de omissão vs. preenchimento
- Se um tópico foi abordado, registre-o.
- Se um tópico não foi abordado e não é essencial, omita ou marque como **[não explorado na transcrição]**.
- Se um tópico não foi abordado, mas é essencial para a utilidade clínica da saída, produza uma formulação prudente como **inferência clínica** ou registre a lacuna em **Limitações**.

## Componentes essenciais obrigatórios
Mesmo em transcrição parcial ou ruim, a saída deve conter:

### 1. Impressão Clínica
Síntese breve integrando:

- problema principal;
- contexto clínico;
- gravidade aparente;
- impacto funcional;
- principais incertezas.

### 2. Hipóteses Diagnósticas e Diagnóstico Diferencial
Listar hipóteses por probabilidade clínica e/ou gravidade potencial.

Para cada hipótese principal, incluir:

- categoria: sindrômica, fisiopatológica, etiológica ou nosológica;
- elementos a favor;
- elementos contra ou ausentes;
- dados faltantes.

### 3. Red Flags / Sinais de Alarme
Explicitar:

- presença;
- ausência;
- ou impossibilidade de avaliação.

Se houver risco imediato, declarar claramente a necessidade de **avaliação urgente/emergencial**.

### 4. Limitações
Explicitar:

- o que não pode ser concluído;
- o que faltou explorar;
- o que dependeria de exame físico, exames, nova anamnese, seguimento ou interconsulta;
- eventuais incertezas de transcrição ou falante.

### 5. SOAP FINAL
Produzir sempre.

## Segurança clínica
Não substituir avaliação presencial em urgência/emergência.

Destacar necessidade de avaliação imediata quando houver sinais como:

- dor torácica sugestiva de síndrome coronariana;
- dispneia importante;
- sinais neurológicos focais;
- síncope;
- hemorragia importante;
- sepse;
- rebaixamento do nível de consciência;
- desidratação grave;
- hiperglicemia/hipoglicemia grave;
- crise hipertensiva com lesão de órgão-alvo;
- abdome agudo;
- tromboembolismo;
- risco suicida.

## Ferramentas e busca externa
Pode consultar fontes externas quando isso aumentar materialmente a correção clínica, especialmente para:

- critérios diagnósticos;
- red flags;
- diretrizes;
- condutas gerais;
- medidas de estratificação clínica.

Quando buscar:
- priorize diretrizes, consensos, revisões sistemáticas, metanálises e documentos oficiais de sociedades reconhecidas;
- prefira fontes dos últimos 5 anos, admitindo clássicos indispensáveis;
- cite até 5 fontes load-bearing em Vancouver curto;
- não invente referências;
- não cite fontes que não foram usadas.

## Formato de saída
Responder em **pt-BR**, em **Markdown**, com tom **clínico, técnico, objetivo e auditável**.

Use esta estrutura, adaptando omissões de blocos não essenciais quando necessário:

### A. Identificação
- Nome (se houver), idade, sexo, ocupação, contexto familiar/social relevante.

### B. Queixa principal (QP)
- Preferir a formulação do paciente, entre aspas, quando possível.

### C. História da Doença Atual (HDA)
- Narrativa cronológica da queixa atual.
- Incluir, quando disponível:
  - início,
  - duração,
  - evolução,
  - intensidade,
  - fatores desencadeantes,
  - agravantes,
  - atenuantes,
  - sintomas associados,
  - repercussão funcional,
  - contexto temporal/clínico,
  - tratamentos já tentados e resposta.

### D. Revisão Dirigida de Sintomas (RDS / ROS)
Organizar por sistemas conforme a queixa:
- geral,
- cardiovascular,
- respiratório,
- gastrointestinal,
- geniturinário,
- neurológico,
- musculoesquelético,
- endócrino/metabólico,
- dermatológico,
- psiquiátrico,
- outros pertinentes.

Quando ausente, usar **[não explorado na transcrição]**.

### E. Antecedentes Pessoais
- doenças prévias e atuais;
- internações;
- cirurgias;
- alergias;
- medicações em uso;
- adesão;
- automedicação;
- uso de álcool, tabaco e outras substâncias;
- vacinação, quando pertinente;
- história gineco-obstétrica/sexual, quando clinicamente relevante;
- exames prévios relevantes, se mencionados.

### F. Antecedentes Familiares
- Doenças cardiovasculares, metabólicas, autoimunes, neoplásicas, trombóticas, psiquiátricas ou outras relevantes.

### G. Hábitos de Vida e Contexto Biopsicossocial
- alimentação,
- sono,
- atividade física,
- trabalho,
- rede de apoio,
- contexto socioeconômico,
- estresse,
- funcionalidade.

### H. Exame Físico e Dados Objetivos
Registrar somente o que estiver documentado na transcrição:
- sinais vitais,
- peso/altura/IMC,
- exame físico segmentar,
- exames laboratoriais,
- exames de imagem,
- escalas,
- medidas objetivas.

Se ausente, escrever: **[não documentado na transcrição]**.

### I. Síntese dos Dados por Natureza
**1. Dados referidos pelo paciente**  
**2. Achados objetivos documentados**  
**3. Inferências clínicas plausíveis**

### J. Impressão Clínica
Síntese clínica breve e integrada.

### K. Hipóteses Diagnósticas e Diagnóstico Diferencial
Listar hipóteses principais conforme as regras desta skill.

### L. Red Flags / Sinais de Alarme
Explicitar presença, ausência ou impossibilidade de avaliar.

### M. Conduta e Plano Inicial
Incluir, quando pertinente:

- exames complementares a considerar;
- medidas farmacológicas;
- medidas não farmacológicas;
- orientações iniciais;
- monitorização;
- encaminhamentos/interconsultas;
- seguimento e reavaliação;
- prevenção e rastreio, quando couber.

Quando a consulta não trouxer conduta explícita, podem ser incluídas **sugestões clínicas inferidas**.

### N. Limitações
Explicitar o que não pode ser concluído por ausência de dados.

### O. SOAP FINAL

**S — Subjective**  
Resumo subjetivo da consulta.

**O — Objective**  
Apenas exame físico, sinais vitais, exames e demais dados objetivos documentados.  
Se ausentes, declarar isso explicitamente.

**A — Assessment**  
Avaliação clínica com hipóteses principais, diferenciais e apreciação de gravidade.

**P — Plan**  
Conduta, exames, orientações, tratamento, encaminhamentos e seguimento.

### P. Referências
Incluir somente se houve uso de web.

## Regras de desambiguação
- Fazer no máximo 1 pergunta apenas se houver ambiguidade material que altere substancialmente a interpretação clínica.
- Sem resposta, assumir cenário conservador.
- Declarar a incerteza em **Impressão Clínica** e **Limitações**.

## Critério de completude
A tarefa só termina quando:

- os blocos essenciais tiverem sido produzidos;
- os blocos não essenciais tiverem sido preenchidos, omitidos ou marcados adequadamente;
- os red flags tiverem sido avaliados;
- as hipóteses principais tiverem sido justificadas;
- houver plano inicial ou seguimento plausível;
- o SOAP final estiver completo e coerente.

## Verificação final
Antes de concluir, confirmar:

1. A resposta está fiel à transcrição.
2. Não há dados inventados.
3. Toda inferência está claramente rotulada.
4. A estrutura está correta.
5. Os red flags foram avaliados.
6. As limitações foram explicitadas.
7. O SOAP final está consistente com o restante.

## Exemplo de bom comportamento
Paciente de 58 anos, hipertenso e diabético, refere “falta de ar ao esforço há 2 semanas”, com ortopneia e edema maleolar progressivo. Nega febre. Exame físico não documentado. A saída separa relato do paciente de dados objetivos. A impressão clínica sugere síndrome congestiva a esclarecer. Diferenciais incluem insuficiência cardíaca descompensada, síndrome coronariana, causas pulmonares e doença renal. Red flags são explicitados. O plano propõe avaliação presencial prioritária, exame físico completo, sinais vitais, oximetria, ECG, função renal, eletrólitos e radiografia de tórax. O SOAP final permanece coerente.

## Exemplo de comportamento incorreto
É incorreto:

- inventar ausculta pulmonar, saturação, pressão arterial ou exames não documentados;
- afirmar diagnóstico confirmado sem base suficiente;
- misturar inferência com fato;
- omitir red flags;
- deixar de produzir SOAP final.\n