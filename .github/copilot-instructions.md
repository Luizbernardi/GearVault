# Instruções para o GitHub Copilot - Projeto Gear Vault

Este documento fornece uma visão geral do projeto Gear Vault, suas funcionalidades, tecnologias utilizadas e diretrizes para o GitHub Copilot auxiliar no desenvolvimento e manutenção do sistema.

## 1. Visão Geral do Projeto

O **Gear Vault** é um sistema projetado para otimizar o gerenciamento de aquisições e controle de estoque de componentes eletrônicos. Seu principal objetivo é reduzir custos, padronizar processos e automatizar a extração de informações de invoices (notas fiscais), garantindo uma gestão eficiente e integrada. O sistema permite o cadastro de compras via upload de invoices, extração automática de dados, revisão manual de informações, gerenciamento (CRUD) de entidades como Fornecedores, Compradores, Projetos, Locais de Armazenamento e Componentes, controle de estoque multi-localização e visualização detalhada de compras e estoque.




## 2. Como o Sistema Funciona

O Gear Vault opera com base nos seguintes fluxos principais:

*   **Cadastro e Gerenciamento de Aquisições:** O sistema permite o upload de invoices, de onde são extraídas informações automaticamente. Essas informações podem ser revisadas e complementadas manualmente. Isso garante que os dados de compra estejam sempre atualizados e precisos.
*   **Controle de Estoque:** O sistema mantém um controle de estoque em tempo real, com suporte a multi-localização. Isso significa que é possível saber a quantidade exata de cada componente e onde ele está armazenado.
*   **Gerenciamento de Entidades:** Entidades como Fornecedores, Compradores, Projetos, Locais de Armazenamento e Componentes (Itens) são gerenciadas através de operações CRUD (Create, Read, Update, Delete), garantindo a integridade e organização dos dados.
*   **Relatórios e Visualização:** O sistema oferece visualização detalhada de compras e do estado atual do estoque, com opções de filtragem e download das invoices originais. Isso facilita a análise e a tomada de decisões.

## 3. Linguagens e Tecnologias Utilizadas

O projeto Gear Vault é desenvolvido utilizando as seguintes linguagens e tecnologias:

*   **Backend:** Python com o framework Django.
*   **Banco de Dados:** SQLite (para desenvolvimento e testes, podendo ser migrado para PostgreSQL ou MySQL em produção).
*   **Outras bibliotecas Python:**
    *   `asgiref`
    *   `sqlparse`
    *   `tzdata`

## 4. Diretrizes para o GitHub Copilot

Ao interagir com o código do projeto Gear Vault, o GitHub Copilot deve considerar as seguintes diretrizes:

*   **Contexto do Django:** Priorize soluções e padrões de código que sigam as melhores práticas do framework Django (modelos, views, URLs, templates, ORM).
*   **Lógica de Negócio:** Compreenda a lógica de gerenciamento de estoque e aquisições para auxiliar na implementação de novas funcionalidades ou na depuração de problemas.
*   **Extração de Invoices:** Esteja ciente da funcionalidade de extração de dados de invoices e como ela se integra com o restante do sistema.
*   **Segurança:** Ao sugerir código relacionado a autenticação, autorização ou manipulação de dados sensíveis, priorize práticas de segurança robustas.
*   **Manutenibilidade:** Sugira código claro, modular e bem documentado, facilitando futuras manutenções e evoluções do sistema.
*   **Testes:** Auxilie na criação de testes unitários e de integração para garantir a robustez das funcionalidades.

