# Homebox como addon de Home Assistant: imagen oficial (Alpine, multi-arch) + run.sh
# que traduce las opciones del addon a variables HBOX_*.
# FROM literal (sin build.yaml ni BUILD_FROM, formato del builder nuevo de HA) para
# que Dependabot pueda actualizar etiqueta y digest. La versión del addon en
# config.yaml la sincroniza .github/workflows/homebox-version.yaml.
FROM ghcr.io/sysadminsmedia/homebox:0.27.1@sha256:9d0b64776c694f018c0ca06faf52105a33ca376024f46bb58e6ab0e2b728bb61

RUN apk add --no-cache jq

COPY run.sh /run.sh
RUN chmod +x /run.sh

# La imagen oficial arranca /app/api directamente; run.sh lo hace tras leer las opciones.
ENTRYPOINT [ "/run.sh" ]
CMD [ ]
