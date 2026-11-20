#!/usr/bin/env bash
# Abre o simulador na janela Qt (a interface atual). Igual ao comando `yubikey`; aceita as mesmas opções.
exec "$(dirname "$(readlink -f "$0")")/bin/yubikey" "$@"
