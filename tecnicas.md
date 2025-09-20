Camada Fundamental: Preparação de Dados e Engenharia de Features
O desempenho de qualquer modelo de Machine Learning é fundamentalmente limitado pela qualidade dos dados de entrada. Para séries temporais financeiras, como o preço do Bitcoin, os dados brutos são inerentemente ruidosos e contêm informações limitadas. A etapa de engenharia de features é, portanto, o processo mais influente para o sucesso do projeto, transformando uma única série de preços em um conjunto de dados multidimensional que captura a dinâmica subjacente do mercado. A alocação de uma porção significativa do tempo do projeto (50-60%) para esta fase é uma decisão estratégica que produzirá os maiores retornos.   

A Criticidade do Pré-processamento
Séries temporais financeiras são caracterizadas pela não estacionariedade, o que significa que suas propriedades estatísticas, como média e variância, mudam ao longo do tempo. Esta característica viola uma suposição fundamental de muitos modelos estatísticos e de ML.   

Normalização e Escalonamento: Antes de alimentar os dados em modelos, especialmente redes neurais e algoritmos baseados em distância, é crucial escalonar as features. O MinMaxScaler do Scikit-learn, que reescala os dados para um intervalo fixo (geralmente 0 a 1), é uma prática padrão que ajuda a acelerar a convergência do treinamento e a melhorar o desempenho do modelo.   

Diferenciação: Uma técnica clássica para tornar uma série temporal estacionária é a diferenciação, que calcula a mudança entre observações consecutivas. Embora eficaz para modelos como o ARIMA, que exigem estacionariedade , a diferenciação pode remover informações valiosas sobre tendências de longo prazo. Modelos mais avançados, como LSTMs, são projetados para aprender diretamente de sequências não estacionárias, muitas vezes tornando a diferenciação agressiva desnecessária ou até mesmo prejudicial.   

Enriquecendo Séries Temporais: Uma Imersão em Features Preditivas
O objetivo é criar um conjunto de variáveis que forneçam ao modelo um contexto rico sobre o estado atual e passado do mercado.

Indicadores Técnicos
A análise técnica é uma disciplina financeira que utiliza dados históricos de mercado para prever movimentos futuros de preços. No contexto de ML, os indicadores técnicos são, na verdade, uma forma sofisticada de engenharia de features. Para a implementação, recomenda-se fortemente a biblioteca    

pandas-ta, uma ferramenta moderna e poderosa que se integra perfeitamente com DataFrames Pandas e oferece mais de 130 indicadores. Sua facilidade de instalação e uso, em comparação com alternativas como    

TA-Lib , a torna a escolha ideal para este projeto.   

O método df.ta.strategy() da biblioteca é particularmente útil, pois permite a aplicação em massa de uma categoria inteira de indicadores (por exemplo, "Momentum", "Volatility") de forma eficiente, utilizando multiprocessamento para acelerar a geração de features. A tabela a seguir detalha um conjunto inicial de indicadores de alto impacto.   

Nome do Indicador	Categoria	Significado Financeiro	Função pandas-ta
Índice de Força Relativa (RSI)	Momentum	Mede a velocidade e a mudança dos movimentos de preços para identificar condições de sobrecompra ou sobrevenda.	df.ta.rsi(length=14)
Convergência/Divergência de Médias Móveis (MACD)	Tendência	Mostra a relação entre duas médias móveis exponenciais de preços, ajudando a identificar mudanças no momento e na direção da tendência.	df.ta.macd()
Bandas de Bollinger (Bollinger Bands)	Volatilidade	Consiste em uma média móvel central mais duas bandas de desvio padrão, que se alargam ou se contraem com base na volatilidade do mercado.	df.ta.bbands(length=20)
On-Balance Volume (OBV)	Volume	Usa o fluxo de volume para prever mudanças no preço das ações. O OBV mede a pressão de compra e venda como um indicador cumulativo.	df.ta.obv()
Average True Range (ATR)	Volatilidade	Mede a volatilidade do mercado, decompondo toda a faixa de preço de um ativo para aquele período.	df.ta.atr(length=14)
Oscilador Estocástico (Stochastic)	Momentum	Compara um preço de fechamento específico com uma gama de seus preços durante um determinado período de tempo, indicando o momento e a força da tendência.	df.ta.stoch()

Exportar para as Planilhas
Features de Atraso (Lagged) e Rolantes (Rolling)
Para modelos que não possuem uma estrutura de memória interna (como redes recorrentes), é essencial fornecer explicitamente informações sobre o passado.

Features de Atraso: Criar colunas que representam o valor de uma feature em um momento anterior (por exemplo, price_lag_1min, price_lag_5min) permite que o modelo veja a trajetória recente do mercado.   

Estatísticas Rolantes: Calcular estatísticas como média móvel, desvio padrão, mínimo e máximo em uma janela de tempo deslizante (por exemplo, rolling_mean_30min, rolling_std_60min) suaviza o ruído de curto prazo e captura tendências e volatilidade locais.   

Features Baseadas no Tempo
O próprio timestamp é uma fonte rica de informação e pode capturar padrões cíclicos. A partir da data/hora de cada registro, podem ser extraídas features como:

Minuto da hora (0-59)

Hora do dia (0-23)

Dia da semana (0-6)

Semana do ano

Essas features podem ajudar o modelo a aprender padrões intradiários ou semanais (por exemplo, maior volatilidade durante o horário de abertura das bolsas de valores tradicionais).

A combinação dessas três categorias de features transformará a série temporal univariada de preços em uma tabela rica e de alta dimensão, pronta para alimentar modelos de ML sofisticados e permitindo-lhes descobrir padrões complexos que seriam invisíveis nos dados brutos.