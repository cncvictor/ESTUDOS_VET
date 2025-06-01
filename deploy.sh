#!/bin/bash

echo "🚀 Iniciando deploy..."

# Adiciona todas as alterações
git add .

# Pega a mensagem do commit como argumento ou usa uma mensagem padrão
if [ -z "$1" ]
then
    commit_message="update: Atualização do sistema"
else
    commit_message="$1"
fi

# Faz o commit
git commit -m "$commit_message"

# Faz o push
git push origin main

echo "✅ Deploy iniciado! Aguarde alguns minutos para as alterações serem aplicadas no Streamlit Cloud." 