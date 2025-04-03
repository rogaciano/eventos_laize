#!/usr/bin/env python
"""
Script de diagnóstico para problemas de atualização no servidor.
Este script verifica várias possíveis causas de problemas de atualização e fornece instruções para resolvê-los.
"""

import os
import sys
import subprocess
import datetime

def run_command(command):
    """Executa um comando e retorna a saída."""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {command}")
        print(f"Saída de erro: {e.stderr}")
        return None

def check_git_status():
    """Verifica o status do Git."""
    print("\n=== Verificando status do Git ===")
    
    # Verificar se há alterações não commitadas
    status = run_command("git status --porcelain")
    if status:
        print("⚠️ Há alterações não commitadas:")
        print(status)
        print("\nVocê precisa commitar essas alterações antes de fazer push:")
        print("git add .")
        print('git commit -m "Adiciona exibição de origem do cadastro e corrige exibição de categorias"')
        print("git push origin main")  # Ajuste a branch conforme necessário
    else:
        print("✅ Não há alterações não commitadas.")
    
    # Verificar a branch atual
    branch = run_command("git branch --show-current")
    print(f"Branch atual: {branch}")
    
    # Verificar último commit
    last_commit = run_command("git log -1 --pretty=format:'%h - %s (%cr)'")
    print(f"Último commit: {last_commit}")

def check_django_settings():
    """Verifica as configurações do Django."""
    print("\n=== Verificando configurações do Django ===")
    
    # Verificar arquivo de configuração
    if os.path.exists("eventos/settings.py"):
        print("✅ Arquivo de configuração principal encontrado: eventos/settings.py")
    else:
        print("❌ Arquivo de configuração principal não encontrado!")
    
    # Verificar arquivos de configuração específicos
    settings_files = ["settings_base.py", "settings_dev.py", "settings_prod.py"]
    for file in settings_files:
        if os.path.exists(file):
            print(f"✅ Arquivo de configuração encontrado: {file}")
            
            # Verificar configurações de cache
            with open(file, "r") as f:
                content = f.read()
                if "CACHES" in content:
                    print(f"  - Configuração de cache encontrada em {file}")
                    
                    # Verificar se está usando FileBasedCache
                    if "FileBasedCache" in content:
                        print("  - Usando FileBasedCache - pode precisar limpar manualmente")
                    
                    # Verificar se está usando MemcachedCache
                    if "MemcachedCache" in content:
                        print("  - Usando MemcachedCache - pode precisar reiniciar o serviço memcached")
                    
                    # Verificar se está usando RedisCache
                    if "RedisCache" in content:
                        print("  - Usando RedisCache - pode precisar limpar o cache do Redis")
        else:
            print(f"❌ Arquivo de configuração não encontrado: {file}")

def check_static_files():
    """Verifica arquivos estáticos."""
    print("\n=== Verificando arquivos estáticos ===")
    
    # Verificar se o diretório static existe
    if os.path.exists("static"):
        print("✅ Diretório static encontrado")
    else:
        print("❌ Diretório static não encontrado!")
    
    # Verificar se o diretório templates existe
    if os.path.exists("templates"):
        print("✅ Diretório templates encontrado")
        
        # Verificar se o arquivo person_detail.html existe
        person_detail_path = "templates/people/person_detail.html"
        if os.path.exists(person_detail_path):
            print(f"✅ Arquivo {person_detail_path} encontrado")
            
            # Verificar a data de modificação
            mod_time = os.path.getmtime(person_detail_path)
            mod_time_str = datetime.datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
            print(f"  - Última modificação: {mod_time_str}")
            
            # Verificar se contém a seção de origem do cadastro
            with open(person_detail_path, "r", encoding="utf-8") as f:
                content = f.read()
                if "Origem do Cadastro" in content:
                    print("  - ✅ Contém a seção 'Origem do Cadastro'")
                else:
                    print("  - ❌ Não contém a seção 'Origem do Cadastro'")
        else:
            print(f"❌ Arquivo {person_detail_path} não encontrado!")
    else:
        print("❌ Diretório templates não encontrado!")

def provide_server_commands():
    """Fornece comandos para executar no servidor."""
    print("\n=== Comandos para executar no servidor ===")
    print("1. Conecte-se ao servidor via SSH")
    print("2. Navegue até o diretório do projeto")
    print("3. Execute os seguintes comandos:")
    print("\n# Atualizar o código do repositório")
    print("git fetch --all")
    print("git reset --hard origin/main  # Isso descarta quaisquer alterações locais no servidor!")
    print("\n# Limpar arquivos .pyc que podem estar causando problemas")
    print("find . -name '*.pyc' -delete")
    print("find . -name '__pycache__' -type d -exec rm -rf {} +")
    print("\n# Limpar o cache de templates")
    print("mkdir -p /tmp/django_cache")
    print("rm -rf /tmp/django_cache/*")
    print("\n# Coletar arquivos estáticos")
    print("python manage.py collectstatic --noinput")
    print("\n# Reiniciar o serviço")
    print("# Se estiver usando systemd:")
    print("sudo systemctl restart gunicorn")
    print("# Se estiver usando supervisor:")
    print("sudo supervisorctl restart eventos")
    print("# Se estiver usando Apache com mod_wsgi:")
    print("touch eventos/wsgi.py")
    print("\n# Verificar logs para erros")
    print("tail -f /var/log/gunicorn/error.log  # Ajuste o caminho conforme necessário")

def main():
    print("=== Diagnóstico de Problemas de Atualização no Servidor ===")
    print(f"Data e hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    check_git_status()
    check_django_settings()
    check_static_files()
    provide_server_commands()
    
    print("\n=== Resumo ===")
    print("Se as alterações não estão sendo aplicadas no servidor, pode ser devido a:")
    print("1. Alterações não foram commitadas e/ou enviadas para o repositório")
    print("2. O servidor está usando uma versão em cache dos templates")
    print("3. Arquivos .pyc antigos estão sendo usados em vez dos arquivos .py atualizados")
    print("4. O serviço não foi reiniciado corretamente")
    print("5. Há erros nos logs que impedem a aplicação de iniciar corretamente")
    print("\nExecute os comandos sugeridos na seção 'Comandos para executar no servidor'")
    print("para resolver esses problemas.")

if __name__ == "__main__":
    main()
