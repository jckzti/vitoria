import json
import os
import requests
import time

def download_flags():
    # Carrega o GeoJSON para saber quais países temos
    try:
        with open('custom.geo.json', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Arquivo custom.geo.json não encontrado.")
        return

    output_dir = os.path.join("assets", "flags")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Baixando bandeiras para {len(data['features'])} países...")
    
    count = 0
    errors = 0
    
    for feature in data['features']:
        props = feature['properties']
        country_name = props.get('name', 'Unknown')
        iso_a2 = props.get('iso_a2')

        # Validação do código ISO
        if not iso_a2 or iso_a2 == -99:
            # Tenta usar wb_a2 ou outra propriedade se iso_a2 falhar
            iso_a2 = props.get('wb_a2')
        
        if not iso_a2 or iso_a2 == -99:
            print(f"Ignorando {country_name}: Código ISO não encontrado.")
            errors += 1
            continue

        iso_a2 = iso_a2.lower() # flagcdn usa minúsculas
        file_path = os.path.join(output_dir, f"{iso_a2}.png")
        
        # Se já existe, pula
        if os.path.exists(file_path):
            count += 1
            continue

        # URL do FlagCDN (formato PNG, largura 80px para ícones leves, ou w160/w320 para maiores)
        # Vamos usar w160 para ter uma qualidade decente no hover
        url = f"https://flagcdn.com/w160/{iso_a2}.png"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"[{count+1}/{len(data['features'])}] Baixado: {country_name} ({iso_a2})")
                count += 1
                # Pequena pausa para ser educado com o servidor
                time.sleep(0.1)
            else:
                print(f"Erro ao baixar {country_name} ({iso_a2}): Status {response.status_code}")
                errors += 1
        except Exception as e:
            print(f"Exceção ao baixar {country_name}: {e}")
            errors += 1

    print(f"\nConcluído! {count} bandeiras prontas. {errors} erros.")

if __name__ == "__main__":
    download_flags()
