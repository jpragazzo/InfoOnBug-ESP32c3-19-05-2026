import json
import os
import esptool
import serial.tools.list_ports



nvs_offset = 0xE000
nvs_size = 0x6000
codigo_inicial = 100000
n_gravacoes = 0
porta = "COM3"
arquivo_nvs_csv = "nvs.csv"
arquivo_nvs_bin = "nvs.bin"
arquivo_flash_lida_bin = "flash_lida.bin"
arquivo_flasher_args = os.path.join(os.path.dirname( __file__ ), '..', 'build', 'flasher_args.json')
nvs_partition_generator_caminho = "C:/Espressif/frameworks/esp-idf-v5.5.4/components/nvs_flash/nvs_partition_generator/nvs_partition_gen.py"



os.system("cls")
print("Portas seriais disponíveis:")
for port in serial.tools.list_ports.comports():
    print(port.name + " | " + port.description + " | " + port.manufacturer + " | " + port.hwid)

print("\n")    
leitura = input("Selecione a porta COM (digite apenas o número): ")
porta = "COM" + leitura.strip()



def apagar_tudo():
    esptool_cmd = ["erase-flash"]
    esptool_cmd.append("--force")
    print("Comando: %s" % " ".join(esptool_cmd))

    try:
        esptool.main(esptool_cmd)
    except Exception as e:
        print("Erro tipo: " + str(type(e)) + " args: " + str(e.args))


    
def ler_flash():
    esptool_cmd = ["-p", porta, "-b", "460800", "read-flash", "0", "0x400000", arquivo_flash_lida_bin]
    print("Comando: %s" % " ".join(esptool_cmd))
    try:
        esptool.main(esptool_cmd)
    except Exception as e:
        print("Erro tipo: " + str(type(e)) + " args: " + str(e.args))
    print("Flash lida para o arquivo " + arquivo_flash_lida_bin)



def image_info():
    print("Selecione o arquivo")
    print("1 - principal")
    print("2 - bootloader")
    print("3 - tabela de partições")
    print("4 - nvs")
    print("5 - flash lida")

    opcao = input("Opção: ")
    opcao = opcao.strip()
    if(opcao == '1'): nome_arquivo = "txbt.bin"
    if(opcao == '2'): nome_arquivo = "bootloader/bootloader.bin"
    if(opcao == '3'): nome_arquivo = "partition_table/partition-table.bin"
    if(opcao == '4'): nome_arquivo = arquivo_nvs_bin
    if(opcao == '5'): nome_arquivo = arquivo_flash_lida_bin
    os.system("cls")

    
    esptool_cmd = ["image-info", "--version", "2", nome_arquivo]
    print("Comando: %s" % " ".join(esptool_cmd))
    try:
        esptool.main(esptool_cmd)
    except Exception as e:
        print("Erro tipo: " + str(type(e)) + " args: " + str(e.args))



def gravar_tudo():
    f = open(arquivo_flasher_args)
    data = json.load(f)
    f.close()


    # HARD RESET REMOVIDO, mesmo erro. 
    #Porta, Baud rate, se há reset antes de flashar, se há depois, e o tipo do chip.
    esptool_cmd = ["-p", porta, "-b", "460800","--before", "default-reset", "--after", "hard-reset","--chip", "esp32c3"]
    
    esptool_cmd.append("write-flash")
    # esptool_cmd.extend(["--flash_mode", data["flash_settings"]["flash_mode"]])
    # esptool_cmd.extend(["--flash_freq", data["flash_settings"]["flash_freq"]])
    # esptool_cmd.extend(["--flash_size", data["flash_settings"]["flash_size"]])
    esptool_cmd.append("--force")
    esptool_cmd.extend(["--flash-mode", "dio"])
    esptool_cmd.extend(["--flash-freq", "40m"])
    esptool_cmd.extend(["--flash-size", "4MB"])
	
    esptool_cmd.extend(["0x0", "../build/enc/bootloader-enc.bin"])
    esptool_cmd.extend(["0xD000", "../build/enc/partition-table-enc.bin"])
    esptool_cmd.extend([str(nvs_offset), arquivo_nvs_bin]) #0xE000
    esptool_cmd.extend(["0x20000", "../build/enc/txbt-enc.bin"])
    # ORIGINALMENTE 0x0, 0x9000, 0xa000 e 0x21000.
    
    print("Comando: %s" % " ".join(esptool_cmd))
    try:
        esptool.main(esptool_cmd)
    except Exception as e:  
        print("Falha! Erro tipo: " + str(type(e)) + " args: " + str(e.args))
        return 0 #adicionado pelo jp
    
    return 1 



def criar_csv_nvs(codigo):
    f = open(arquivo_nvs_csv, "w")
    f.write("key,type,encoding,value\n")
    f.write("storage,namespace,,\n")
    f.write("codigo,data,u32," + str(codigo))
    f.close()



def gerar_bin_particao_nvs():    
    nvs_partition_gen_cmd = "generate " + arquivo_nvs_csv + " " + arquivo_nvs_bin + " " + str(nvs_size)
    try:
        os.system("py " + nvs_partition_generator_caminho + " " + nvs_partition_gen_cmd)
    except Exception as e:
        print("Erro tipo: " + str(type(e)) + " args: " + str(e.args))
    


while(1):
    print("--------------------------------------------------------")
    print("g - gravar")
    print("i - informações")
    print("a - apagar")
    print("l - ler")
    print("s - salvar")
    print("p - sair")
    print("Quantidade gravados: " + str(n_gravacoes))
    print("--------------------------------------------------------\n")
    leitura = input("Comando: ")
    leitura = leitura.strip()

    if(leitura == 'p' or leitura == 'P'): break

    if(leitura == 'a' or leitura == 'A'):
        os.system("cls")
        apagar_tudo()

    if(leitura == 'l' or leitura == 'L'):
        os.system("cls")
        ler_flash()

    if(leitura == 'i' or leitura == 'I'):
        os.system("cls")
        image_info()

    if(leitura == 'g' or leitura == 'G'):
        os.system("cls")
        codigo_atual = codigo_inicial + n_gravacoes
        print("Criando arquivo CSV da NVS com o código: " + str(codigo_atual))
        criar_csv_nvs(codigo_atual)
        gerar_bin_particao_nvs()
        success = gravar_tudo() #adicionado pelo jp pois aqui ele dava sucesso mesmo sem ter sucesso de verdade. 

        if success:
            print("Sucesso na gravação.")
            n_gravacoes += 1

        
    






	


