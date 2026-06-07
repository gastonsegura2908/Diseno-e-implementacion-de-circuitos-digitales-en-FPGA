import time
import serial
import numpy as np
import matplotlib.pyplot as plt
from filtro import RaisedCosineFilter

ser = serial.serial_for_url('loop://', timeout=1)

params = {'alpha': 0.25, 'span': 6, 'sps': 8, 'rrc': True}
filtro = RaisedCosineFilter(**params)

def plot_both():
    taps = filtro.taps
    sps  = filtro.sps
    t    = np.arange(-len(taps) // 2, len(taps) // 2 + 1) / sps

    H = np.fft.fftshift(np.fft.fft(taps, 1024))
    f = np.linspace(-0.5, 0.5, len(H), endpoint=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))

    ax1.plot(t[:len(taps)], taps)
    ax1.set_title("Dominio del tiempo")
    ax1.set_xlabel("Tiempo [periodos de simbolo]")
    ax1.set_ylabel("Amplitud")
    ax1.grid(True)

    ax2.plot(f, 20 * np.log10(np.abs(H) + 1e-6))
    ax2.set_title("Dominio de la frecuencia")
    ax2.set_xlabel("Frecuencia normalizada")
    ax2.set_ylabel("Magnitude [dB]")
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

def plot_discrete():
    taps = filtro.taps
    sps  = filtro.sps
    t    = np.arange(-len(taps) // 2, len(taps) // 2 + 1) / sps

    plt.figure(figsize=(10, 4))
    plt.stem(t[:len(taps)], taps)
    plt.title("Respuesta al Impulso Discreta")
    plt.xlabel("Tiempo [periodos de simbolo]")
    plt.ylabel("Amplitud")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_multi():
    alphas = [0.1, 0.25, 0.5, 0.75, 1.0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))

    for a in alphas:
        f_temp = RaisedCosineFilter(alpha=a, span=params['span'], sps=params['sps'], rrc=params['rrc'])
        taps   = f_temp.taps
        sps    = f_temp.sps
        t      = np.arange(-len(taps) // 2, len(taps) // 2 + 1) / sps

        H = np.fft.fftshift(np.fft.fft(taps, 1024))
        f = np.linspace(-0.5, 0.5, len(H), endpoint=False)

        ax1.plot(t[:len(taps)], taps, label=f"α={a}")
        ax2.plot(f, 20 * np.log10(np.abs(H) + 1e-6), label=f"α={a}")

    ax1.set_title("Dominio del tiempo - Filtros multiples")
    ax1.set_xlabel("Tiempo [periodos de simbolo]")
    ax1.set_ylabel("Amplitud")
    ax1.legend()
    ax1.grid(True)

    ax2.set_title("Dominio de la frecuencia - Filtros multiples")
    ax2.set_xlabel("Frecuencia normalizada")
    ax2.set_ylabel("Magnitud [dB]")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

def procesar_comando(cmd):
    global filtro, params
    partes = cmd.strip().split()

    if not partes:
        print("Comando vacío.")
        return

    if partes[0] == 'set':
        if len(partes) != 3:
            print("Uso: set <parametro> <valor>")
            return

        key = partes[1]
        val = partes[2]

        if key == 'alpha':
            params['alpha'] = float(val)
        elif key == 'span':
            params['span'] = int(val)
        elif key == 'sps':
            params['sps'] = int(val)
        elif key == 'rrc':
            params['rrc'] = val.lower() == 'true'
        else:
            print(f"Parámetro desconocido: {key}")
            return

        filtro = RaisedCosineFilter(**params)
        print(f"Filtro actualizado: {params}")

    elif partes[0] == 'plot':
        if len(partes) != 2:
            print("Uso: plot <time|freq|both|discrete|multi>")
            return

        modo = partes[1]
        if modo == 'time':
            filtro.plot(time_domain=True, freq_domain=False)
        elif modo == 'freq':
            filtro.plot(time_domain=False, freq_domain=True)
        elif modo == 'both':
            plot_both()
        elif modo == 'discrete':
            plot_discrete()
        elif modo == 'multi':
            plot_multi()
        else:
            print(f"Modo de plot desconocido: {modo}")

    elif partes[0] == 'get':
        if len(partes) == 2 and partes[1] == 'coef':
            print(filtro.get_coefficients())
        else:
            print("Uso: get coef")

    elif partes[0] == 'status':
        print(f"Parámetros actuales: {params}")

    else:
        print(f"Comando desconocido: {partes[0]}")

while True:
    data = input("Comando: ")

    if data == 'exit':
        if ser.isOpen():
            ser.close()
        break

    ser.write(data.encode())
    time.sleep(0.1)

    out = ''
    while ser.inWaiting() > 0:
        out += ser.read(1).decode()

    if out:
        procesar_comando(out)