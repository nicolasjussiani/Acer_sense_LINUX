# -*- coding: utf-8 -*-

import customtkinter
import psutil
import subprocess
import re  # Usado para extrair dados da GPU
import os  # Usado para manipulação de ficheiros e permissões
import json  # Usado para guardar e carregar configurações

# =================================================================================
# ARQUIVO DE CONFIGURAÇÃO
# =================================================================================
# As configurações agora são guardadas num ficheiro para persistência
CONFIG_FILE = os.path.expanduser("~/.config/nitrosense_linux_settings.json")
# =================================================================================


# --- Configurações da Aparência ---
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")


class NitroSenseLinux(customtkinter.CTk):
    """
    Classe principal da versão autónoma do Nitro Sense para Linux.
    Esta versão interage diretamente com os ficheiros do sistema (sysfs).
    """

    def __init__(self):
        super().__init__()

        # --- Configuração da Janela Principal ---
        self.title("Nitro Sense (Linux Standalone Edition)")
        self.geometry("850x650")
        self.resizable(False, False)

        # --- Carregar configurações ou usar valores por defeito -
        self._load_settings()

        # --- Layout Principal com Grid -
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Abas para Navegação ---
        self.tab_view = customtkinter.CTkTabview(self, width=250)
        self.tab_view.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.tab_view.add("Dashboard")
        self.tab_view.add("Configurações Avançadas")

        # --- Criação dos Widgets ---
        self.dashboard_tab = self.tab_view.tab("Dashboard")
        self.dashboard_tab.grid_columnconfigure((0, 1), weight=1)
        self._create_monitoring_widgets(self.dashboard_tab)
        self._create_fan_control_widgets(self.dashboard_tab)

        self.settings_tab = self.tab_view.tab("Configurações Avançadas")
        self.settings_tab.grid_columnconfigure(0, weight=1)
        self._create_settings_widgets(self.settings_tab)

        # --- Barra de Status
        self.status_bar = customtkinter.CTkLabel(self, text="Status: Pronto. Monitoramento iniciado.", anchor="w")
        self.status_bar.grid(row=1, column=0, padx=20, pady=(5, 10), sticky="ew")

        self._update_fan_control_ui_state()

        self.update_stats()

    def _load_settings(self):
        """Carrega as configurações de um ficheiro JSON."""
        try:
            with open(CONFIG_FILE, "r") as f:
                settings = json.load(f)
                self.fan_mode_path = settings.get("fan_mode_path", "")
                self.fan_speed_path = settings.get("fan_speed_path", "")
        except (FileNotFoundError, json.JSONDecodeError):
            self.fan_mode_path = ""
            self.fan_speed_path = ""

    def _save_settings(self):
        """Guarda as configurações num ficheiro JSON."""
        self.fan_mode_path = self.mode_path_entry.get()
        self.fan_speed_path = self.speed_path_entry.get()

        settings = {
            "fan_mode_path": self.fan_mode_path,
            "fan_speed_path": self.fan_speed_path,
        }
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings, f, indent=4)

        self.status_bar.configure(text="Configurações guardadas! A verificar caminhos...", text_color="cyan")
        self._update_fan_control_ui_state()

    def _update_fan_control_ui_state(self):
        """Ativa ou desativa os controlos com base na existência dos ficheiros de configuração."""
        is_path_valid = self.fan_mode_path and os.path.exists(self.fan_mode_path)

        new_state = "normal" if is_path_valid else "disabled"

        if hasattr(self, 'auto_button'):
            self.auto_button.configure(state=new_state)
            self.max_button.configure(state=new_state)
        if hasattr(self, 'custom_fan_slider'):
            self.custom_fan_slider.configure(state=new_state)

        if is_path_valid:
            self.status_bar.configure(text="Controle de ventoinha ativado.", text_color="green")
        else:
            self.status_bar.configure(text="Controle de ventoinha desativado. Use as 'Configurações Avançadas'.",
                                      text_color="orange")

    def _create_monitoring_widgets(self, parent_tab):
        monitoring_frame = customtkinter.CTkFrame(parent_tab, fg_color="transparent")
        monitoring_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        monitoring_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.cpu_usage_label = customtkinter.CTkLabel(monitoring_frame, text="Utilização CPU",
                                                      font=customtkinter.CTkFont(size=16))
        self.cpu_usage_label.grid(row=0, column=0, pady=(10, 0))
        self.cpu_usage_value = customtkinter.CTkLabel(monitoring_frame, text="-- %",
                                                      font=customtkinter.CTkFont(size=30, weight="bold"))
        self.cpu_usage_value.grid(row=1, column=0)
        self.cpu_progress = customtkinter.CTkProgressBar(monitoring_frame)
        self.cpu_progress.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.gpu_usage_label = customtkinter.CTkLabel(monitoring_frame, text="Utilização GPU",
                                                      font=customtkinter.CTkFont(size=16))
        self.gpu_usage_label.grid(row=0, column=1, pady=(10, 0))
        self.gpu_usage_value = customtkinter.CTkLabel(monitoring_frame, text="-- %",
                                                      font=customtkinter.CTkFont(size=30, weight="bold"))
        self.gpu_usage_value.grid(row=1, column=1)
        self.gpu_progress = customtkinter.CTkProgressBar(monitoring_frame)
        self.gpu_progress.grid(row=2, column=1, padx=20, pady=(0, 10), sticky="ew")
        self.ram_usage_label = customtkinter.CTkLabel(monitoring_frame, text="Utilização RAM",
                                                      font=customtkinter.CTkFont(size=16))
        self.ram_usage_label.grid(row=0, column=2, pady=(10, 0))
        self.ram_usage_value = customtkinter.CTkLabel(monitoring_frame, text="-- %",
                                                      font=customtkinter.CTkFont(size=30, weight="bold"))
        self.ram_usage_value.grid(row=1, column=2)
        self.ram_progress = customtkinter.CTkProgressBar(monitoring_frame)
        self.ram_progress.grid(row=2, column=2, padx=20, pady=(0, 10), sticky="ew")
        self.cpu_temp_label = customtkinter.CTkLabel(monitoring_frame, text="Temp. CPU",
                                                     font=customtkinter.CTkFont(size=16))
        self.cpu_temp_label.grid(row=3, column=0, pady=(20, 0))
        self.cpu_temp_value = customtkinter.CTkLabel(monitoring_frame, text="-- °C",
                                                     font=customtkinter.CTkFont(size=30, weight="bold"))
        self.cpu_temp_value.grid(row=4, column=0, pady=(0, 10))
        self.gpu_temp_label = customtkinter.CTkLabel(monitoring_frame, text="Temp. GPU",
                                                     font=customtkinter.CTkFont(size=16))
        self.gpu_temp_label.grid(row=3, column=1, pady=(20, 0))
        self.gpu_temp_value = customtkinter.CTkLabel(monitoring_frame, text="-- °C",
                                                     font=customtkinter.CTkFont(size=30, weight="bold"))
        self.gpu_temp_value.grid(row=4, column=1, pady=(0, 10))

    def _create_fan_control_widgets(self, parent_tab):
        """Cria os widgets de controle de ventoinha."""
        fan_control_frame = customtkinter.CTkFrame(parent_tab)
        fan_control_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=20, sticky="nsew")
        fan_control_frame.grid_columnconfigure((0, 1), weight=1)

        fan_title_label = customtkinter.CTkLabel(fan_control_frame, text="Controle da Ventoinha",
                                                 font=customtkinter.CTkFont(size=18, weight="bold"))
        fan_title_label.grid(row=0, column=0, columnspan=2, pady=(15, 10))

        # Adiciona os botões e o slider, que serão ativados/desativados depois
        self.auto_button = customtkinter.CTkButton(fan_control_frame, text="Automático", height=40,
                                                   command=lambda: self._write_to_sysfs(self.fan_mode_path, "0"))
        self.auto_button.grid(row=1, column=0, padx=(20, 5), pady=10, sticky="ew")

        self.max_button = customtkinter.CTkButton(fan_control_frame, text="Máximo", height=40, fg_color="#D20000",
                                                  hover_color="#AA0000",
                                                  command=lambda: self._write_to_sysfs(self.fan_mode_path, "1"))
        self.max_button.grid(row=1, column=1, padx=(5, 20), pady=10, sticky="ew")

        custom_slider_label = customtkinter.CTkLabel(fan_control_frame, text="Modo Customizado:")
        custom_slider_label.grid(row=2, column=0, columnspan=2, pady=(20, 0))

        self.custom_fan_slider = customtkinter.CTkSlider(fan_control_frame, from_=0, to=255,
                                                         command=lambda v: self._write_to_sysfs(self.fan_speed_path,
                                                                                                str(int(v))))
        self.custom_fan_slider.set(128)
        self.custom_fan_slider.grid(row=3, column=0, columnspan=2, padx=30, pady=(5, 20), sticky="ew")

    def _create_settings_widgets(self, parent_tab):
        """Cria os widgets da aba de configurações."""
        diag_frame = customtkinter.CTkFrame(parent_tab)
        diag_frame.pack(pady=10, padx=10, fill="x")
        diag_label = customtkinter.CTkLabel(diag_frame, text="Diagnóstico do Sistema",
                                            font=customtkinter.CTkFont(size=16))
        diag_label.pack(pady=10)
        self.diag_status_label = customtkinter.CTkLabel(diag_frame, text="Status: Pendente", text_color="gray")
        self.diag_status_label.pack(pady=(0, 10))
        check_module_button = customtkinter.CTkButton(diag_frame, text="Verificar Módulo do Kernel (acer-wmi)",
                                                      command=self._check_kernel_module)
        check_module_button.pack(pady=(0, 15))

        path_frame = customtkinter.CTkFrame(parent_tab)
        path_frame.pack(pady=10, padx=10, fill="x")
        path_label = customtkinter.CTkLabel(path_frame, text="Caminhos do Controlo de Hardware (sysfs)",
                                            font=customtkinter.CTkFont(size=16))
        path_label.pack(pady=(10, 5))

        auto_find_button = customtkinter.CTkButton(path_frame, text="Procurar Automaticamente",
                                                   command=self._auto_find_paths)
        auto_find_button.pack(pady=10)

        mode_path_label = customtkinter.CTkLabel(path_frame, text="Ficheiro do Modo da Ventoinha (0=Auto, 1=Max):")
        mode_path_label.pack(pady=(10, 0))
        self.mode_path_entry = customtkinter.CTkEntry(path_frame,
                                                      placeholder_text="Clique em 'Procurar Automaticamente' ou insira o caminho manual",
                                                      width=400)
        self.mode_path_entry.insert(0, self.fan_mode_path)
        self.mode_path_entry.pack(pady=(0, 10), padx=20)

        speed_path_label = customtkinter.CTkLabel(path_frame, text="Ficheiro da Velocidade da Ventoinha (0-255):")
        speed_path_label.pack(pady=(10, 0))
        self.speed_path_entry = customtkinter.CTkEntry(path_frame,
                                                       placeholder_text="Clique em 'Procurar Automaticamente' ou insira o caminho manual",
                                                       width=400)
        self.speed_path_entry.insert(0, self.fan_speed_path)
        self.speed_path_entry.pack(pady=(0, 15), padx=20)

        save_button = customtkinter.CTkButton(path_frame, text="Guardar Configurações", command=self._save_settings)
        save_button.pack(pady=(0, 15))

    def _check_kernel_module(self):
        """Verifica se o módulo do kernel 'acer-wmi' está carregado"""
        self.diag_status_label.configure(text="Verificando...", text_color="yellow")
        try:
            result = subprocess.run(['lsmod'], capture_output=True, text=True, check=True)
            if 'acer_wmi' in result.stdout:
                self.diag_status_label.configure(text="Sucesso! Módulo 'acer_wmi' está carregado.", text_color="green")
            else:
                self.diag_status_label.configure(
                    text="Módulo 'acer_wmi' não encontrado.\nTente executar 'sudo modprobe acer-wmi' num terminal.",
                    text_color="orange", wraplength=400)
        except Exception as e:
            self.diag_status_label.configure(text=f"Erro ao verificar módulo: {e}", text_color="red")

    def _auto_find_paths(self):
        """Procura automaticamente por ficheiros de controlo de ventoinha comuns"""
        self.status_bar.configure(text="Procurando por ficheiros de controlo...", text_color="yellow")
        base_path = "/sys/devices/platform/"
        found_mode = ""
        found_speed = ""

        try:
            for root, dirs, files in os.walk(base_path):
                if 'acer-wmi' in root:  # Procura mais focada
                    if "fan_mode" in files:
                        found_mode = os.path.join(root, "fan_mode")
                    if "fan_speed" in files:
                        found_speed = os.path.join(root, "fan_speed")
                if found_mode and found_speed:
                    break
        except Exception as e:
            self.status_bar.configure(text=f"Erro durante a procura: {e}", text_color="red")
            return

        if found_mode:
            self.mode_path_entry.delete(0, "end")
            self.mode_path_entry.insert(0, found_mode)
            self.status_bar.configure(text="Caminhos encontrados! Clique em 'Guardar' para aplicar.", text_color="cyan")
        else:
            self.status_bar.configure(
                text="Nenhum ficheiro 'fan_mode' encontrado. Verifique se o módulo 'acer-wmi' está carregado.",
                text_color="orange")

        if found_speed:
            self.speed_path_entry.delete(0, "end")
            self.speed_path_entry.insert(0, found_speed)

        if not found_mode and not found_speed:
            self.status_bar.configure(text="Nenhum ficheiro de controlo de ventoinha conhecido foi encontrado.",
                                      text_color="red")

    def _get_cpu_stats(self):

        cpu_percent = psutil.cpu_percent(interval=None)
        self.cpu_usage_value.configure(text=f"{cpu_percent:.1f} %")
        self.cpu_progress.set(cpu_percent / 100)
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                core_temp = temps['coretemp'][0].current
                self.cpu_temp_value.configure(text=f"{core_temp:.1f} °C")
            else:
                self.cpu_temp_value.configure(text="N/A")
        except Exception:
            self.cpu_temp_value.configure(text="Erro")

    def _get_gpu_stats(self):
        # gpu difere
        try:
            command = "nvidia-smi --query-gpu=temperature.gpu,utilization.gpu --format=csv,noheader,nounits"
            result = subprocess.check_output(command, shell=True, text=True)
            temp, usage = result.strip().split(', ')
            self.gpu_temp_value.configure(text=f"{float(temp):.1f} °C")
            self.gpu_usage_value.configure(text=f"{float(usage):.1f} %")
            self.gpu_progress.set(float(usage) / 100)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.gpu_temp_value.configure(text="N/A")
            self.gpu_usage_value.configure(text="N/A")
            self.gpu_progress.set(0)
        except Exception as e:
            print(f"Erro ao ler GPU: {e}")
            self.gpu_temp_value.configure(text="Erro")
            self.gpu_usage_value.configure(text="Erro")
            self.gpu_progress.set(0)

    def _get_ram_stats(self):
        # (O código para as estatísticas de RAM permanece o mesmo)
        ram = psutil.virtual_memory()
        self.ram_usage_value.configure(text=f"{ram.percent:.1f} %")
        self.ram_progress.set(ram.percent / 100)

    def update_stats(self):
        """Função principal que atualiza todas as estatísticas na UI."""
        self._get_cpu_stats()
        self._get_gpu_stats()
        self._get_ram_stats()
        self.after(1500, self.update_stats)

    def _write_to_sysfs(self, file_path: str, value: str):
        """
        Escreve um valor num ficheiro de sistema (sysfs) com privilégios de root.
        Usa 'tee' com 'pkexec' para redirecionar a escrita de forma segura.
        """
        if not file_path or not os.path.exists(file_path):
            self.status_bar.configure(text=f"Erro: Caminho do ficheiro inválido ou não configurado.", text_color="red")
            return

        try:
            command = ['pkexec', 'tee', file_path]
            print(f"EXECUTANDO COMANDO: echo {value} | {' '.join(command)}")

            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True)
            stdout, stderr = process.communicate(input=value)

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

            self.status_bar.configure(text=f"Valor '{value}' escrito com sucesso em '{os.path.basename(file_path)}'.",
                                      text_color="green")

        except FileNotFoundError:
            error_msg = f"Erro: 'pkexec' ou 'tee' não encontrado. Verifique a sua instalação."
            print(error_msg)
            self.status_bar.configure(text=error_msg, text_color="red")
        except subprocess.CalledProcessError as e:
            error_msg = f"Falha ao escrever no ficheiro. Erro: {e.stderr.strip()}"
            print(error_msg)
            self.status_bar.configure(text=error_msg, text_color="red")
        except Exception as e:
            error_msg = f"Um erro inesperado ocorreu: {e}"
            print(error_msg)
            self.status_bar.configure(text=error_msg, text_color="red")


if __name__ == "__main__":
    try:
        import psutil
    except ImportError:
        print("Erro: psutil não encontrado. Por favor, instale com 'pip install psutil'")
        exit()

    app = NitroSenseLinux()
    app.mainloop()

