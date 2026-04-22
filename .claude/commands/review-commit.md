Revise as mudanças staged antes do commit chamando um agente externo (OpenAI).

Siga estes passos em ordem:

1. Execute `git diff --cached` e capture o output
2. Se o output estiver vazio, informe: "Nenhuma mudança staged. Rode `git add` primeiro." e pare
3. Salve o diff em `/tmp/petregister_review.txt`
4. Execute `python3 scripts/review_commit.py /tmp/petregister_review.txt`
5. Apresente o resultado exatamente como retornado pelo script
6. Delete o arquivo temporário com `rm /tmp/petregister_review.txt`

Se o script retornar erro, verifique se as dependências estão instaladas:
`pip3 install openai python-dotenv`

E se OPENAI_API_KEY está definida no .env da raiz do projeto.
