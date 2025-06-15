# Nitro Sense para Linux (Edição Standalone)

![Screenshot da Aplicação](URL_PARA_UMA_IMAGEM_AQUI) <!-- Opcional: Tire uma screenshot da app e carregue-a para o GitHub para colocar o link aqui -->

Uma aplicação de código aberto, feita em Python com CustomTkinter, para monitorizar e controlar hardware em portáteis Acer (Nitro/Predator) que correm Linux.

## Motivação

Este projeto nasceu da necessidade de ter uma ferramenta semelhante ao Acer NitroSense no ambiente Linux, uma vez que a Acer não oferece suporte oficial. O objetivo é criar uma solução autónoma que interage diretamente com o sistema (`sysfs`) sem depender de binários externos.

## Funcionalidades

* **Monitorização em Tempo Real:**
    * Utilização e Temperatura da CPU.
    * Utilização e Temperatura da GPU (NVIDIA).
    * Utilização da Memória RAM.
* **Controlo de Ventoinha:**
    * Modos Automático e Máximo.
    * Controlo de velocidade personalizado através de um slider.
* **Configuração Inteligente:**
    * Ferramenta de diagnóstico para verificar o módulo do kernel `acer-wmi`.
    * Função de procura automática para encontrar os ficheiros de controlo de hardware.
    * Interface para configurar manualmente os caminhos dos ficheiros de sistema (`sysfs`).
* **Interface Moderna:** Construída com a biblioteca CustomTkinter para um visual agradável e moderno.

## Instalação e Utilização

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/nicolasjussiani/Acer_sense_LINUX.git](https://github.com/nicolasjussiani/Acer_sense_LINUX.git)
    cd Acer_sense_LINUX
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute a aplicação:**
    ```bash
    python nitro_sense_linux.py
    ```

4.  **Configuração Inicial:**
    * Na primeira vez que executar, os controlos de ventoinha estarão desativados.
    * Vá à aba **"Configurações Avançadas"**.
    * Use o botão **"Verificar Módulo do Kernel"** para garantir que o `acer-wmi` está ativo. Se não estiver, siga as instruções.
    * Clique em **"Procurar Automaticamente"** para que a aplicação encontre os ficheiros de controlo.
    * Se forem encontrados, clique em **"Guardar Configurações"**. Os controlos no Dashboard serão ativados.

## Licença

Este projeto está licenciado sob a **Licença MIT**. Veja o ficheiro [LICENSE](LICENSE) para mais detalhes.
