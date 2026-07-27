## 📌 Visão Geral do Projeto

Este projeto foi desenvolvido para identificar clientes com perfil **VIP** que apresentam sinais de risco de abandono (*churn*), permitindo que a empresa adote ações preventivas de retenção antes do encerramento do ciclo de compra. 

A iniciativa utiliza dados públicos do e-commerce brasileiro da **Olist**, abrangendo cerca de **100 mil pedidos** realizados entre 2016 e 2018, para mapear o comportamento de compra, avaliar o valor do tempo de vida do cliente (*LTV*) e apoiar tomadas de decisão estratégicas por meio de visualizações interativas.

---

## 🧭 Como Navegar no Dashboard

O dashboard foi estruturado para conduzir o usuário em uma jornada lógica de análise, partindo de um **panorama executivo** até o detalhamento de **alavancas operacionais e de retenção**.

A sequência das abas foi projetada para responder às principais perguntas de negócio:

* **📊 1. Visão Geral:** Apresenta o panorama executivo e os principais KPIs do e-commerce, oferecendo uma leitura rápida e clara do desempenho geral da operação.
* **📈 2. Evolução Temporal:** Mapeia a trajetória do negócio ao longo do tempo, destacando tendências de crescimento, sazonalidades e padrões de comportamento de compra por horário.
* **🏷️ 3. Receita por Categorias e Produtos:** Identifica quais categorias e produtos concentram o faturamento da plataforma e onde residem as maiores oportunidades comerciais.
* **🚚 4. Logística e Atrasos:** Avalia a eficiência operacional das entregas, medindo o impacto do desempenho logístico e dos atrasos na experiência e satisfação do cliente.
* **🎯 5. Concentração de Receita:** Conclui a análise detalhando a distribuição do faturamento pela base de clientes (Curva de Pareto / Princípio 80/20) e evidenciando a dependência da empresa em relação aos perfis de maior valor.

* ## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.13
* **Interface & Framework:** Streamlit
* **Banco de Dados & API:** Supabase (API REST)
* **Visualização de Dados:** Plotly Express & Pandas
* **Autenticação & RBAC:** Streamlit-Authenticator (BCrypt)
