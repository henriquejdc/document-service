# Desafio Técnico de Python

No século XXI, a informação é um dos bens mais valiosos para as grandes instituições. Depois da Revolução Técnico-Científica, as forma como a humanidade enxerga os dados se transformou radicalmente, impactando tanto nos aspectos práticos quanto subjetivos da nossa existência. 

As grandes instituições entendem os dados com um bem extremamente valioso, pelo potencial de geração de valor através de sua análise. **Nesse contexto, encontrar os dados corretos para cada ocasião é fundamental.**

**Seu objetivo é construir um microsserviço que seja capaz de encontrar as informações adequadas, dado uma palavra-chave.**

## Especificação

- Seu microsserviço deve ser construído em **Python** 3.x, e deve seguir os padrões **REST** com **HTTP**.
- **O framework para construir a API é de livre escolha.**
- Dois endpoints devem ser desenvolvidos, conforme descrito abaixo.

### Criar um novo Documento

O primeiro endpoint deverá receber dados que representam um documento, com o método POST e conteúdo no formato JSON, conforme o exemplo a seguir.

```json
{
    "titulo": "Titulo do meu documento",
    "autor": "Autor do documento",
    "conteudo": "Esse é o conteúdo do meu documento. Ele pode conter somente texto, e as informações aqui dentro podem ser extensas...",
    "data": "2025-01-01"
}
```

Esse documento deverá ser persistido em um banco de dados **que não seja em memória**, para consulta posterior. **Não é permitido o uso de ElasticSearch, Apache Solr, Sphinx ou serviços similares.** **O banco deverá ser tradicional (como Postgres, Oracle, MongoDB, e etc.).** 

### Buscar por documentos com palavra-chave

O segundo endpoint deverá receber um único dado via parâmetro de query (*query param*), denominado `palavraChave`. Esse parâmetro conterá uma palavra-chave qualquer, e o endpoint deverá retornar uma lista de documentos que contenham aquela palavra-chave. Por exemplo:

Requisição: 

```
GET /documentos?palavraChave=informação
```

Resposta:

```json
[
    {
        "titulo": "Os impactos sociais na Era da informação",
        "autor": "...",
        "conteudo": "...",
        "data": "2025-01-01"
    },
    {
        "titulo": "...",
        "autor": "João, Mestre em Sistemas de Informação",
        "conteudo": "...",
        "data": "2025-02-01"
    },
    {
        "titulo": "...",
        "autor": "...",
        "conteudo": "Existe um sério risco relacionado à informação.",
        "data": "2025-01-01"
    }
]
```

## Tarefas bônus

### Tarefa Bônus 1 - Ordenação por Localização

O ponto deste desafio é obter informações de forma mais adequada possível. Em vista disso, os documentos terão mais dois atributos obrigatórios, latitude e longitude, com o objetivo de ordenar as informações de forma mais eficaz. 

Segue um exemplo para criação de documentos com esses novos campos:

```json
{
    "titulo": "Titulo do meu documento",
    "autor": "Autor do documento",
    "conteudo": "Esse é o conteúdo do meu documento. Ele pode conter somente texto, e as informações aqui dentro podem ser extensas...",
    "data": "2025-01-01",
    "latitude": -30.05968294264794,
    "longitude": -51.171757376504914
}
```

As coordenadas estão em Graus Decimais (GD).

Ao buscar por documentos dado uma palavra-chave, o usuário poderá informar, de forma opcional, uma latitude e longitude nos parâmetros, conforme o seguinte exemplo:

```
GET /documentos?palavraChave=carro&latitude=-29.990000&longitude=-51.170000
```

Com esses parâmetros, o microsserviço deverá, em ordem:

1. Realizar a busca dos documentos pela palavra-chave, sem utilizar da localização.
2. Ordenar os documentos de acordo com a proximidade geográfica da localização passada na requisição, do mais próximo ao mais distante.

Para o exemplo anterior, poderíamos ter esse resultado:

```json
[
  // documento mais proximo
  {
    "titulo": "Como consertar um carro antigo",
    "autor": "João Mecânico",
    "conteudo": "Este documento explica como restaurar veículos clássicos, incluindo dicas sobre peças e pintura.",
    "data": "2025-01-01",
    "latitude": "...",
    "longitude": "..."
  },

  // segundo documento mais proximo
  {
    "titulo": "História do automóvel no Brasil",
    "autor": "Maria Historiadora",
    "conteudo": "Um estudo detalhado sobre a evolução dos carros no Brasil desde o século XX.",
    "data": "2024-11-15",
    "latitude": "...",
    "longitude": "..."
  },

  // terceiro documento mais próximo
  {
    "titulo": "Guia de bicicletas urbanas",
    "autor": "Carlos Ciclista",
    "conteudo": "Este guia foca em bicicletas, mas menciona brevemente carros como alternativa urbana.",
    "data": "2025-03-10",
    "latitude": "...",
    "longitude": "..."
  }
]
```

### Tarefa Bônus 2 - Busca por expressões

Até o momento, o microsserviço é somente capaz de buscar por uma palavra especifica. No entanto, os grandes mecanismos de busca, como o Google, permitem que os usuários passem uma frase ao invés de uma única palavra.

Seu objetivo, nessa segunda tarefa bônus, é permitir que a busca possa ser realizada com uma frase, e não somente uma palavra. 

Por exemplo:

```
GET /documentos?busca=Carros+antigos+em+porto+alegre
```

```json
[
    {
        "titulo": "Novo encontro de Antiguidades!",
        "autor": "...",
        "conteudo": "Nessa sexta-feira (08), acontecerá o encontro de histórico carros antigos na cidade de Porto Alegre. Todos são bem vindos!",
        "data": "2025-01-01",
    },
    // ...
]
```

## O que será avaliado no desafio?

- **Performance;**
- Estratégias usadas para implementação do desafio;
- Organização do código;
- Arquitetura do projeto;
- Boas práticas de programação (manutenibilidade, legibilidade e etc);
- Possíveis bugs;
- Tratamento de erros e exceções;
- Explicação breve do porquê das escolhas tomadas durante o desenvolvimento da solução;
- Documentação do código e da API;
- Logs da aplicação;
- Mensagens e organização dos commits;
- Testes;

## Dicas

- Teste bem sua solução. Evite bugs!
- Não inicie o teste sem sanar todas as dúvidas.
- Iremos executar a aplicação para testá-la, cuide com qualquer dependência externa e deixe claro caso haja instruções especiais para execução do mesmo.
- Existem diversas formas de resolver esse desafio. Implemente a que faz mais sentido para você, como desenvolvedor web ou cientista de dados!