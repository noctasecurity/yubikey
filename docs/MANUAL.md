<p align="center"><img src="img/logo.png" alt="yksim por noctasecurity" width="480"></p>

# Manual do yksim

O **yksim** é uma YubiKey 5 NFC virtual (firmware 5.8.0) com o applet PIV, escrita em Python. Ele serve para
desenvolver e testar aplicações que usam PIV ou smart card sem precisar de uma chave física. O `ykman`, o OpenSC
(PKCS#11) e qualquer aplicativo PC/SC enxergam o yksim como uma chave de verdade:

```
$ ykman list
YubiKey 5 NFC (5.8.0) [OTP+FIDO+CCID] Serial: 29013790
```

![Janela do yksim](img/janela.png)

Funciona no Debian e no Ubuntu do WSL2 (Windows). O yksim é um projeto da [NoctaSecurity](https://github.com/noctasecurity),
sem vínculo com a Yubico; veja o [Aviso](#18-aviso) no fim.

## Sumário

1. [Como funciona](#1-como-funciona)
2. [O que é emulado](#2-o-que-é-emulado)
3. [Dependências](#3-dependências)
4. [Instalação no Debian](#4-instalação-no-debian)
5. [Instalação no WSL2 (Windows)](#5-instalação-no-wsl2-windows)
6. [Primeiro uso](#6-primeiro-uso)
7. [Tutorial: chave PIV com o ykman e o OpenSC](#7-tutorial-chave-piv-com-o-ykman-e-o-opensc)
8. [Toque](#8-toque)
9. [PIN, PUK e bloqueio](#9-pin-puk-e-bloqueio)
10. [Várias chaves](#10-várias-chaves)
11. [Interface web](#11-interface-web)
12. [App cliente de teste](#12-app-cliente-de-teste)
13. [Linha de comando](#13-linha-de-comando)
14. [Uso em testes automatizados](#14-uso-em-testes-automatizados)
15. [Arquivos e dados](#15-arquivos-e-dados)
16. [Solução de problemas](#16-solução-de-problemas)
17. [Sobre](#17-sobre)
18. [Aviso](#18-aviso)

## 1. Como funciona

![Arquitetura: aplicativos, pcscd, vpcd e yksim](img/arquitetura.svg)

- Os aplicativos falam PC/SC com o serviço `pcscd`, como fariam com uma YubiKey USB.
- O driver `vsmartcard-vpcd` cria um leitor de cartão virtual dentro do `pcscd` e repassa cada comando (APDU)
  por TCP, na porta `127.0.0.1:35963`.
- O yksim se conecta a essa porta e responde como uma YubiKey 5 NFC com firmware 5.8.0.
- **LIGAR** e **DESLIGAR** na janela equivalem a plugar e desplugar a chave na porta USB.

O leitor virtual se chama `Yubico YubiKey OTP+FIDO+CCID (yksim)`. O nome importa: o `ykman` só lista leitores
com "Yubico YubiKey" no nome e deduz dele o modo `[OTP+FIDO+CCID]`.

## 2. O que é emulado

| Applet | Suporte |
|---|---|
| Gerenciamento | `ykman list` e `ykman info` (serial, firmware 5.8.0, formato, capacidades USB e NFC), `ykman config usb/nfc` |
| PIV | PIN e PUK (contadores, bloqueio, desbloqueio, troca); chave de gerenciamento TDES, AES128, AES192 ou AES256 (padrão AES192, como no firmware 5.7 em diante); geração e importação de RSA 1024 a 4096, ECCP256, ECCP384, Ed25519 e X25519; assinatura, decifração RSA e ECDH; políticas de PIN (NEVER, ONCE, ALWAYS) e de toque; metadados; atestação (slot F9); mover e apagar chaves; objetos de dados (certificados, CHUID, objetos protegidos por PIN); reset; encadeamento de APDU e APDUs estendidas |

OTP e FIDO não são emulados: aparecem só como capacidades no `ykman info`.

**Limitações importantes**

- **Atestação:** é assinada por uma CA de teste gerada localmente, não pela CA da Yubico. Serviços que validam
  atestação genuína vão rejeitá-la, e isso é intencional.
- **Segurança:** as chaves privadas ficam sem criptografia em `~/.local/share/yksim/<serial>.json`, com permissão
  600. Não use para chaves reais.
- **Visibilidade:** a chave só existe para o Linux onde o `pcscd` roda. No WSL, os programas do Windows não a veem.
- **Toque:** é simulado, com um clique na janela, aprovação automática ou a opção `--touch` no modo terminal.

## 3. Dependências

O `setup.sh` instala tudo isto. A tabela serve para conferir ou para instalar à mão.

| Para quê | Debian 13 (trixie) | Ubuntu 24.04 no WSL2 |
|---|---|---|
| Serviço PC/SC | `pcscd` | `pcscd` |
| Leitor virtual | `vsmartcard-vpcd` | `vsmartcard-vpcd` (repositório universe) |
| Diagnóstico (`pcsc_scan`) | `pcsc-tools` | `pcsc-tools` |
| PKCS#11 (`pkcs11-tool`) | `opensc` | `opensc` |
| Python e venv | `python3`, `python3-venv` | `python3`, `python3-venv` |
| Janela Qt (padrão) | `python3-pyside6.qtwidgets` | PySide6 pelo pip no venv (o `setup.sh` faz isso) |
| Janela Tk (antiga) | `python3-tk` | `python3-tk` |
| Gerenciador de serviços | systemd (já vem) | systemd ativado no `/etc/wsl.conf` (seção 5) |
| Janela gráfica | X11 ou Wayland do desktop | WSLg (Windows 11, ou Windows 10 com `wsl --update`) |
| Abrir o navegador do Windows (opcional) | — | `wslu` (`wslview`) |

Bibliotecas Python (`requirements.txt`, instaladas no venv): `cryptography`, `yubikey-manager` (inclui o `ykman`),
`pyscard` e `pytest`. Se o pip precisar compilar o `pyscard`, instale também
`swig libpcsclite-dev build-essential python3-dev`.

## 4. Instalação no Debian

```sh
git clone https://github.com/noctasecurity/yubikey.git
cd yubikey
./setup.sh
```

O `setup.sh` usa `sudo` para:

1. instalar os pacotes da seção 3;
2. renomear o leitor virtual em `/etc/reader.conf.d/vpcd` para `Yubico YubiKey OTP+FIDO+CCID (yksim)` (para outro
   nome, rode `READER_NAME="..." ./setup.sh`);
3. tirar o `--auto-exit` do `pcscd`, que fazia o serviço encerrar depois de 60 s parado e "desplugar" a chave
   virtual;
4. reiniciar o `pcscd`.

Depois, sem `sudo`, ele cria a `.venv` do projeto (com `--system-site-packages`, para aproveitar o PySide6 do
sistema), instala as bibliotecas Python e cria o comando `yubikey` em `~/.local/bin`.

<details>
<summary>Instalação manual, sem o setup.sh</summary>

```sh
sudo apt-get install -y pcscd pcsc-tools vsmartcard-vpcd opensc python3-venv python3-tk python3-pyside6.qtwidgets
sudo sed -i 's|^FRIENDLYNAME .*|FRIENDLYNAME "Yubico YubiKey OTP+FIDO+CCID (yksim)"|' /etc/reader.conf.d/vpcd
sudo mkdir -p /etc/systemd/system/pcscd.service.d
printf '[Service]\nExecStart=\nExecStart=/usr/sbin/pcscd --foreground $PCSCD_ARGS\n' |
  sudo tee /etc/systemd/system/pcscd.service.d/yksim.conf
sudo systemctl daemon-reload && sudo systemctl restart pcscd.socket pcscd.service
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
ln -sf "$PWD/bin/yubikey" ~/.local/bin/yubikey
```

</details>

## 5. Instalação no WSL2 (Windows)

Pré-requisitos no Windows: WSL2 com Ubuntu 24.04 e WSLg (já vem no Windows 11; no Windows 10, rode `wsl --update`
no PowerShell). Não é preciso o `usbipd`: a chave é virtual, então não há USB para repassar.

1. Ative o systemd, porque o `pcscd` depende dele. No Ubuntu do WSL:

    ```sh
    printf '[boot]\nsystemd=true\n' | sudo tee /etc/wsl.conf
    ```

    No PowerShell, rode `wsl --shutdown`. Abra o Ubuntu de novo e confira com `systemctl is-system-running`
    (a resposta deve ser `running` ou `degraded`).

2. Instale como no Debian:

    ```sh
    git clone https://github.com/noctasecurity/yubikey.git
    cd yubikey
    ./setup.sh
    ```

    Se o systemd não estiver ativo, o `setup.sh` para logo no início e mostra o passo 1.

3. Opcional: para a interface web abrir no navegador do Windows,

    ```sh
    sudo apt-get install -y wslu
    echo 'export BROWSER=wslview' >> ~/.bashrc
    ```

    Sem isso, abra `http://localhost:8765` no navegador do Windows.

## 6. Primeiro uso

Abra o simulador:

```sh
yubikey
```

O que observar na janela:

- **LED** em volta do disco dourado:
    - apagado: desligada;
    - âmbar piscando: esperando o `pcscd` e o `vpcd`;
    - verde: conectada (pisca a cada APDU);
    - verde piscando rápido: esperando um toque.
- **Conexão:** deve mostrar "conectada ao pcscd".
- **PIN e PUK** ficam sempre visíveis, com as tentativas restantes.
- **Log:** cada APDU recebida aparece com o código de resposta (`9000` é sucesso; vermelho é erro).
- **Sobre** (botão no topo, ou F1): o que é o yksim e quem é a NoctaSecurity.

Em outro terminal, confira que a chave aparece:

```sh
.venv/bin/ykman list
.venv/bin/ykman info
```

> Se houver uma YubiKey física conectada, use sempre `--device <serial>` nos comandos do `ykman`, para não mexer
> nela por engano.

## 7. Tutorial: chave PIV com o ykman e o OpenSC

Os valores padrão são PIN `123456`, PUK `12345678` e chave de gerenciamento
`010203040506070801020304050607080102030405060708` (AES192). Troque `SERIAL` pelo serial da sua chave virtual.

```sh
alias yk='.venv/bin/ykman --device SERIAL'

# 1. Estado do applet PIV
yk piv info

# 2. Gerar um par ECC P-256 no slot 9a (a chave privada nunca sai da "chave")
yk piv keys generate -a ECCP256 --pin-policy ONCE --touch-policy NEVER 9a pub.pem

# 3. Criar e gravar um certificado autoassinado para o slot (pede o PIN)
yk piv certificates generate -s "CN=teste yksim" 9a pub.pem

# 4. Atestação: prova que a chave foi gerada dentro do dispositivo
yk piv keys attest 9a att.pem
yk piv certificates export f9 f9.pem
.venv/bin/python -m yksim --serial SERIAL --export-ca ca.pem      # CA de teste desta chave
openssl verify -CAfile ca.pem -untrusted f9.pem att.pem           # att.pem: OK
```

Pelo PKCS#11, com o OpenSC (o slot 9a é o objeto de ID `01`):

```sh
P11=/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so
pkcs11-tool --module $P11 -L        # lista o leitor e o token
pkcs11-tool --module $P11 -O        # lista certificados e chaves
echo "olá" > msg.txt
pkcs11-tool --module $P11 --login --pin 123456 --sign -m ECDSA-SHA256 --id 01 -i msg.txt -o assinatura.bin
```

## 8. Toque

Uma chave gerada com `--touch-policy ALWAYS` (ou `CACHED`) exige um toque a cada uso. Quando isso acontece, a janela
mostra **TOQUE NA CHAVE** em amarelo, com o slot e a contagem regressiva de 15 s, e o LED pisca rápido:

![Toque pendente](img/toque.png)

- Clique no disco dourado ou aperte **Espaço**.
- Sem toque em 15 s, a operação falha, como na chave física.
- `CACHED` dispensa um novo toque por 15 s.
- **Tocar automaticamente** aprova todos os toques, o que ajuda em testes repetitivos.

## 9. PIN, PUK e bloqueio

Três PINs errados bloqueiam o PIN, como numa YubiKey real. A janela mostra **BLOQUEADO** em vermelho:

![PIN bloqueado](img/pin-bloqueado.png)

- **Pelo caminho real:** `ykman piv access unblock-pin -u 12345678 -n 123456` (usa o PUK).
- **Atalho do simulador:** o botão **Restaurar tentativas de PIN/PUK** volta os contadores ao máximo e desbloqueia o
  PIN e o PUK, sem mudar os valores. Numa chave física isso não existe: um PUK bloqueado não tem volta.
- **Trocar os valores:** `ykman piv access change-pin` e `ykman piv access change-puk`. A janela mostra os valores
  novos e deixa de indicar "valor padrão".

## 10. Várias chaves

Cada chave virtual é um arquivo `~/.local/share/yksim/<serial>.json`, e só uma fica "plugada" por vez, porque há um
único leitor virtual.

- **Chave:** o seletor no topo da janela troca a chave no leitor. É como tirar uma YubiKey da porta e colocar outra:
  o `pcscd` vê a remoção e a inserção.
- **Nova chave:** cria uma chave com serial aleatório de exatamente 8 dígitos, sem repetir um existente, com a sua
  própria CA de atestação de teste.
- A janela abre na última chave usada. `yubikey --serial 12345678` abre (ou cria) uma chave específica.
- Pelo terminal: `.venv/bin/python -m yksim --list` e `.venv/bin/python -m yksim --new`.
- Para apagar uma chave: `rm ~/.local/share/yksim/<serial>.json`, com o simulador fechado.

## 11. Interface web

`yubikey --web` abre a mesma interface no navegador, em `http://localhost:8765`:

![Interface web](img/web.png)

Ela tem os mesmos controles da janela Qt, com uma diferença: a tecla **L** liga e desliga, no lugar de Ctrl+P. O
**Sobre** abre com o botão no topo ou com F1.

A interface web foi feita para que nenhum site aberto no navegador consiga mexer na chave:

- escuta só em `127.0.0.1` e recusa pedidos que não venham de `localhost`;
- só aceita comandos em JSON, que um formulário de outro site não consegue enviar;
- não pode ser carregada dentro de outra página (cabeçalhos contra clickjacking), então ninguém consegue esconder o
  disco dourado numa página e induzir um toque.

Mesmo assim, a janela Qt não abre porta nenhuma e continua sendo a opção mais segura. Se a porta 8765 já estiver em
uso por outro programa, feche esse programa ou use a janela Qt.

O botão **Configurar sistema (setup.sh)** existe só na janela Qt. Ele roda o `setup.sh` e mostra a saída no log, mas
só quando o `sudo` funciona sem senha; caso contrário, rode `./setup.sh` no terminal.

## 12. App cliente de teste

`tests/app_cliente.py` é um aplicativo Qt que pede a YubiKey como um aplicativo real faria, só pelo `pcscd`. Serve
para conferir o simulador de ponta a ponta:

```sh
python3 tests/app_cliente.py       # com o simulador aberto e ligado
```

![App cliente de teste](img/app-cliente.png)

1. **Procurar YubiKey:** lista os leitores PC/SC e as chaves que responderam.
2. **Verificar PIN:** confere o PIN e mostra as tentativas restantes.
3. **Gerar chave no slot:** ECC P-256 com PIN e toque sempre exigidos, usando a chave de gerenciamento padrão.
   Atenção: sobrescreve o que houver no slot.
4. **Assinar desafio:** assina 32 bytes aleatórios e confere a assinatura com a chave pública do slot. Se o slot
   exigir toque, toque no simulador.

Ele não é um teste do pytest e não roda junto com `pytest tests`.

## 13. Linha de comando

Comando `yubikey`, criado pelo `setup.sh` (o `yksim-gui.sh` na pasta do projeto faz o mesmo):

```sh
yubikey              # janela Qt em segundo plano (log em ~/.local/state/yksim/gui.log)
yubikey --fg         # o mesmo, preso ao terminal, mostrando os logs
yubikey --web        # interface no navegador (http://localhost:8765)
yubikey --tk         # janela Tk (antiga; não troca de chave)
yubikey --terminal   # sem interface
yubikey --off        # abre com a chave desligada
yubikey --serial N   # abre a chave N (8 dígitos; cria se não existir)
yubikey --stop       # fecha o simulador
```

Modo terminal (`python -m yksim`):

| Opção | Efeito |
|---|---|
| `--serial N` | abre a chave N; cria se não existir (exatamente 8 dígitos) |
| `--new` | cria uma chave com serial aleatório |
| `--list` | lista as chaves e sai |
| `--dir DIR` | diretório das chaves (padrão `~/.local/share/yksim`) |
| `--state ARQ` | usa um arquivo avulso, fora do diretório de chaves |
| `--touch auto\|deny\|prompt` | como responder aos pedidos de toque |
| `--export-ca ARQ` | grava a CA de atestação de teste e sai |
| `-v` / `-vv` | log; `-vv` mostra cada APDU e os comandos do vpcd |

A janela e o modo terminal usam os mesmos arquivos de chave: não rode os dois ao mesmo tempo.

## 14. Uso em testes automatizados

Para testes não é preciso o `pcscd`: o `SimConnection` liga o `yubikit` direto ao simulador, em memória.

```python
from yksim import open_sim
from yksim.testing import SimConnection
from yubikit.piv import PivSession, DEFAULT_MANAGEMENT_KEY, SLOT, KEY_TYPE

piv = PivSession(SimConnection(open_sim()))        # só em memória; serial aleatório de 8 dígitos
piv.authenticate(DEFAULT_MANAGEMENT_KEY)
pub = piv.generate_key(SLOT.AUTHENTICATION, KEY_TYPE.ECCP256)
```

```sh
.venv/bin/python -m pytest -q tests                              # todos
.venv/bin/python -m pytest -q tests/test_sim.py::test_pin_flow   # um só
```

Se o pytest falhar ao carregar (por exemplo `module 'PySide6' has no attribute 'QtTest'`), algum plugin instalado no
sistema, como o `pytest-qt`, está atrapalhando. Rode com `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` na frente.

## 15. Arquivos e dados

| Caminho | Conteúdo |
|---|---|
| `~/.local/share/yksim/<serial>.json` | uma chave: serial, PIN e PUK com os contadores, chave de gerenciamento, chaves privadas de cada slot (PEM, sem criptografia), objetos PIV e a CA de teste; permissão 600 |
| `~/.local/state/yksim/gui.log` | saída do simulador quando aberto com `yubikey` em segundo plano |
| `/etc/reader.conf.d/vpcd` | configuração do leitor virtual (nome alterado pelo `setup.sh`) |
| `/etc/systemd/system/pcscd.service.d/yksim.conf` | `pcscd` sem `--auto-exit` |

Para recomeçar do zero: `yubikey --stop && rm ~/.local/share/yksim/*.json`.

## 16. Solução de problemas

| Sintoma | Causa provável e solução |
|---|---|
| LED âmbar piscando sem parar | O vpcd não está instalado ou o `pcscd` não está rodando. Rode `./setup.sh` e confira `systemctl status pcscd`. |
| `ykman list` vazio, mas o `pcsc_scan` mostra o leitor | O nome do leitor não contém "Yubico YubiKey". Rode `./setup.sh` de novo (ou ajuste `FRIENDLYNAME` em `/etc/reader.conf.d/vpcd`) e reinicie o `pcscd`. |
| A chave "some" depois de um minuto parada | `pcscd` com `--auto-exit`. O `setup.sh` remove essa opção. |
| `Card is unpowered` ou "nenhuma YubiKey respondeu", com o leitor visível | Outro programa PC/SC está usando o cartão ao mesmo tempo (por exemplo o OpenSC carregado pelo navegador ou pelo `gnome-keyring`). Clique em **DESLIGAR** e **LIGAR** no simulador e tente de novo. |
| O `setup.sh` para dizendo que o systemd não está ativo (WSL) | Ative o systemd (seção 5, passo 1) e rode `wsl --shutdown`. |
| A janela não abre no WSL | Falta o WSLg: atualize com `wsl --update` e confira `echo $DISPLAY`. Como alternativa, use `yubikey --web`. |
| Programas do Windows não veem a chave | Esperado: a chave só existe dentro do Linux do WSL. |
| **Configurar sistema** diz que o sudo pede senha | O botão não tem onde digitar a senha. Rode `./setup.sh` no terminal. |
| `yubikey --web` não abre ou dá erro de porta | A porta 8765 está em uso por outro programa. Feche esse programa ou use a janela Qt. |

## 17. Sobre

![Sobre o yksim e a NoctaSecurity](img/sobre.png)

O yksim faz parte das ferramentas da **NoctaSecurity**, uma empresa brasileira de segurança da informação.
Acreditamos que nenhuma ação crítica deve acontecer sem uma pessoa presente para aprová-la, a mesma ideia de uma
chave de segurança física, que só assina quando alguém encosta o dedo. Por isso as nossas cores são o preto e o
amarelo dessas chaves, e o símbolo do yksim são os anéis do toque gravados no disco dourado.

- Código: <https://github.com/noctasecurity/yubikey>
- NoctaSecurity: <https://github.com/noctasecurity>

## 18. Aviso

YubiKey é marca registrada da Yubico AB. O yksim é um projeto independente, sem vínculo com a Yubico e sem endosso
dela. Use só para desenvolvimento e testes: as chaves simuladas ficam em arquivos comuns no disco e a CA de atestação
é de teste, então nada disso tem a proteção de hardware de uma YubiKey de verdade.
