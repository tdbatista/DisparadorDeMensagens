CONFIGURAÇÕES:

CHROMEDRIVER_PATH   Caminho do chromeDriver , para saber mais va em: https://developer.chrome.com/docs/chromedriver/downloads?hl=pt-br
CAMINHO_IMAGEM  Caminho da imagem a  ser disparada, esse script foi com a ideia de disparar imagem, se for colocar texto, teria que fazer algumas mudanças
CONTACTS_CSV contatos em CSV que ficam guardados na sua conta do google. Vá em contatos e exporte como CSV e ele estará compatível com o script.
SENT_LOG nome do arquivo a ser gerado para log e controle

# Delays (ajuste se necessário), são delays a cada etapa da automação, para que der tempo de carregar corretamente a página
DELAY_AFTER_SEARCH = 2 
DELAY_AFTER_OPEN_CHAT = 2
DELAY_BEFORE_ATTACH = 1
DELAY_AFTER_ATTACH = 3
DELAY_BETWEEN_CONTACTS = 2

MAX_SENDS_PER_DAY    -  Quantidade de disparos por dia ou por vez que rodar o programa. Como rodo ele 1 x ao dia. 
INTERVALDO_DE_DIAS = 30    Intervalo de dias que não disparará, isso evita spammar para o mesmo cliente a mensagem, voce pode diminuir se necessario
INTERVALO_ENTRE_DISPAROS = 5    Isso aqui é importante para o Zuck não bloquear, coloquei 5 pois normalmente é o que uma pessoa faria manuamente, mandadno 5 por vez
DURACAO_INTERVALO = 300    Duração de segundos do intervalo entre os disparos, tudo isso para evitar um block do zap.
