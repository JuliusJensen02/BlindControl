cd ../ || exit 1


py -u -m main_predict --room='1.213' --period="winter" --interval=1
py -u -m main_predict --room='1.213' --period="winter" --interval=4
py -u -m main_predict --room='1.213' --period="winter" --interval=12
py -u -m main_predict --room='1.213' --period="winter" --interval=24

py -u -m main_predict --room='1.213' --period="spring" --interval=1
py -u -m main_predict --room='1.213' --period="spring" --interval=4
py -u -m main_predict --room='1.213' --period="spring" --interval=12
py -u -m main_predict --room='1.213' --period="spring" --interval=24

py -u -m main_predict --room='1.213' --period="december" --interval=1
py -u -m main_predict --room='1.213' --period="december" --interval=4
py -u -m main_predict --room='1.213' --period="december" --interval=12
py -u -m main_predict --room='1.213' --period="december" --interval=24

py -u -m main_predict --room='1.213' --period="january" --interval=1
py -u -m main_predict --room='1.213' --period="january" --interval=4
py -u -m main_predict --room='1.213' --period="january" --interval=12
py -u -m main_predict --room='1.213' --period="january" --interval=24

py -u -m main_predict --room='1.213' --period="february" --interval=1
py -u -m main_predict --room='1.213' --period="february" --interval=4
py -u -m main_predict --room='1.213' --period="february" --interval=12
py -u -m main_predict --room='1.213' --period="february" --interval=24

py -u -m main_predict --room='1.213' --period="march" --interval=1
py -u -m main_predict --room='1.213' --period="march" --interval=4
py -u -m main_predict --room='1.213' --period="march" --interval=12
py -u -m main_predict --room='1.213' --period="march" --interval=24

py -u -m main_predict --room='1.213' --period="april" --interval=1
py -u -m main_predict --room='1.213' --period="april" --interval=4
py -u -m main_predict --room='1.213' --period="april" --interval=12
py -u -m main_predict --room='1.213' --period="april" --interval=24

