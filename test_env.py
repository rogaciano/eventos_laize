import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Obter o valor da variável ENABLE_WHATSAPP
enable_whatsapp = os.getenv('ENABLE_WHATSAPP', 'False')
print(f"Valor bruto: {enable_whatsapp}")
print(f"Tipo: {type(enable_whatsapp)}")

# Verificar se o valor é considerado como True
is_true = enable_whatsapp.lower() in ('true', 't', '1', 'yes', 'y')
print(f"É considerado True? {is_true}")

# Verificar se o valor é considerado como False
is_false = enable_whatsapp.lower() in ('false', 'f', '0', 'no', 'n')
print(f"É considerado False? {is_false}")
