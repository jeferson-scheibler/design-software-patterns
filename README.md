Demonstração de Design Patterns
Este projeto é uma pequena aplicação web criada para demonstrar o funcionamento de três padrões de projeto (Design Patterns) de forma interativa: Singleton, Factory Method e Observer.

A aplicação foi desenvolvida com HTML, JavaScript puro e Tailwind CSS para a estilização, contida em um único arquivo (index.html) para simplificar a implantação e o entendimento.

Patterns Implementados
1. Singleton
Objetivo: Garantir que uma classe tenha apenas uma única instância e fornecer um ponto de acesso global para ela.

Na Aplicação: A classe ConfigManager é implementada como um Singleton. Não importa quantas vezes o botão "Obter Instância" seja clicado, a mesma instância do gerenciador de configurações é retornada. Isso é útil para gerenciar estados globais, como configurações de tema, conexões de banco de dados, etc., sem desperdiçar recursos criando múltiplos objetos.

2. Factory Method
Objetivo: Definir uma interface para criar um objeto, mas permitir que as subclasses alterem o tipo de objetos que serão criados.

Na Aplicação: Uma NotificationFactory é responsável por criar diferentes tipos de objetos de notificação (Email, SMS, Push). O código cliente não precisa saber os detalhes de como cada notificação é instanciada. Ele apenas solicita à fábrica o tipo de notificação desejado, desacoplando o cliente das classes concretas.

3. Observer
Objetivo: Definir uma dependência do tipo "um-para-muitos" entre objetos, de forma que, quando um objeto (o Subject) muda de estado, todos os seus dependentes (os Observers) são notificados e atualizados automaticamente.

Na Aplicação: Temos uma Newsletter (o Subject) e vários Assinantes (os Observers). Quando uma nova notícia é publicada na newsletter ao clicar no botão, todos os assinantes inscritos são notificados instantaneamente e atualizam sua interface para exibir o título da nova notícia.

Como Executar
Clonar o repositório:

git clone [https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git](https://github.com/SEU-USUARIO/SEU-REPOSITORIO.git)

Abrir o arquivo index.html:

Navegue até a pasta do projeto e abra o arquivo index.html diretamente em qualquer navegador web (Chrome, Firefox, etc.).

(Opcional) Publicar com GitHub Pages:

Faça o push do código para o seu repositório no GitHub.

Vá em Settings > Pages.

Na seção Build and deployment, selecione a branch main (ou master) e a pasta /root.

Salve e aguarde alguns minutos. Sua aplicação estará disponível em https://SEU-USUARIO.github.io/SEU-REPOSITORIO/.

Este projeto foi criado como parte de um trabalho acadêmico para demonstrar a aplicação prática de Design Patterns.
