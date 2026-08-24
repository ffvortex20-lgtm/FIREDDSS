# Firebase Test - GitHub

Versao do teste controlado que antes era executado no Termux.

## Configuracao

1. Crie um repositorio no GitHub.
2. Envie `main.py` e a pasta `.github/workflows/`.
3. No repositorio, abra:
   `Settings -> Secrets and variables -> Actions`.
4. Crie o secret `FIREBASE_URL` com a URL do seu proprio Realtime Database.
5. Abra `Actions -> Firebase Test -> Run workflow`.
6. Preencha os parametros e execute.

## Limites desta versao

Para evitar que um teste acidental consuma memoria/recursos excessivos:
- Peso: ate 5 MB por envio
- Conexoes: ate 5
- Intervalo minimo: 1000 ms
- Duracao: ate 60000 ms

O log mostra `ENVIANDO`, HTTP, latencia, sucessos e erros.
