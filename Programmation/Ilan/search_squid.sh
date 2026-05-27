#!/bin/bash
# search_squid.sh — Recherche dans les archives Squid/OPNsense stockées par Wazuh
# Usage: ./search_squid.sh -h

ARCHIVES="/var/lib/docker/volumes/single-node_wazuh_logs/_data/archives"

usage() {
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -i <ip>           Filtrer par IP source"
    echo "  -u <url>          Filtrer par URL ou domaine"
    echo "  -d <YYYY-MM-DD>   Rechercher sur un jour précis"
    echo "  -f <YYYY-MM-DD>   Date de début (plage)"
    echo "  -t <YYYY-MM-DD>   Date de fin   (plage)"
    echo "  -o <fichier>      Sauvegarder les résultats dans un fichier"
    echo "  -c <fichier>      Exporter les résultats en CSV"
    echo "  -h                Afficher cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 -i 192.168.1.10"
    echo "  $0 -u facebook.com"
    echo "  $0 -i 192.168.1.10 -u youtube.com"
    echo "  $0 -i 192.168.1.10 -d 2026-04-15"
    echo "  $0 -u facebook.com -f 2026-03-01 -t 2026-03-31"
    echo "  $0 -i 192.168.1.10 -u facebook.com -f 2026-03-01 -t 2026-03-31 -o export.txt"
    echo "  $0 -i 192.168.1.10 -f 2026-03-01 -t 2026-03-31 -c export.csv"
    echo ""
    exit 0
}

# Vérifier que jq est installé
if ! command -v jq &>/dev/null; then
    echo "❌ jq n'est pas installé. Lance : apt install jq"
    exit 1
fi

# Defaults
FILTER_IP=""
FILTER_URL=""
DATE_SPECIFIC=""
DATE_FROM=""
DATE_TO=""
OUTPUT=""
CSV=""

# Parse des arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -i) FILTER_IP="$2";       shift 2 ;;
        -u) FILTER_URL="$2";      shift 2 ;;
        -d) DATE_SPECIFIC="$2";   shift 2 ;;
        -f) DATE_FROM="$2";       shift 2 ;;
        -t) DATE_TO="$2";         shift 2 ;;
        -o) OUTPUT="$2";          shift 2 ;;
        -c) CSV="$2";             shift 2 ;;
        -h) usage ;;
        *)  echo "❌ Option inconnue : $1"; usage ;;
    esac
done

# Au moins un filtre obligatoire
if [[ -z "$FILTER_IP" && -z "$FILTER_URL" ]]; then
    echo "❌ Tu dois spécifier au moins une IP (-i) ou une URL (-u)."
    usage
fi

# Construire le filtre jq — on ne garde que les logs Squid d'OPNsense
JQ_FILTER='.location == "/var/log/squid/access.log"'

[[ -n "$FILTER_IP" ]]  && JQ_FILTER+=" and (.data.source.ip // \"\" | contains(\"$FILTER_IP\"))"
[[ -n "$FILTER_URL" ]] && JQ_FILTER+=" and (.data.url.original // \"\" | ascii_downcase | contains(\"$(echo "$FILTER_URL" | tr '[:upper:]' '[:lower:]')\"))"

# Sélectionner les fichiers selon la date
select_files() {
    local all_files=()

    if [[ -n "$DATE_SPECIFIC" ]]; then
        # Convertir YYYY-MM-DD en Year/MonthName
        local year month_num month_name
        year=$(echo "$DATE_SPECIFIC" | cut -d'-' -f1)
        month_num=$(echo "$DATE_SPECIFIC" | cut -d'-' -f2)
        month_name=$(date -d "${DATE_SPECIFIC}-01" +%b 2>/dev/null || date -jf "%Y-%m-%d" "${DATE_SPECIFIC}" +%b 2>/dev/null)
        local day
        day=$(echo "$DATE_SPECIFIC" | cut -d'-' -f3 | sed 's/^0//')
        local pattern="ossec-archive-$(printf '%02d' "$day")"
        while IFS= read -r f; do
            all_files+=("$f")
        done < <(find "$ARCHIVES/$year/$month_name" -name "${pattern}*" 2>/dev/null | sort)

    elif [[ -n "$DATE_FROM" && -n "$DATE_TO" ]]; then
        # Parcourir toutes les dates dans la plage
        local current="$DATE_FROM"
        while [[ "$current" < "$DATE_TO" ]] || [[ "$current" == "$DATE_TO" ]]; do
            local year month_num month_name day
            year=$(echo "$current" | cut -d'-' -f1)
            month_name=$(date -d "$current" +%b 2>/dev/null)
            day=$(echo "$current" | cut -d'-' -f3 | sed 's/^0//')
            local pattern="ossec-archive-$(printf '%02d' "$day")"
            while IFS= read -r f; do
                all_files+=("$f")
            done < <(find "$ARCHIVES/$year/$month_name" -name "${pattern}*" 2>/dev/null | sort)
            current=$(date -d "$current + 1 day" +%Y-%m-%d)
        done

    else
        # Tous les fichiers
        while IFS= read -r f; do
            all_files+=("$f")
        done < <(find "$ARCHIVES" -type f -name "*.json.gz" -o -name "*.json" | grep -v "\.sum$" | sort)
    fi

    printf '%s\n' "${all_files[@]}"
}

# Lire un fichier (compressé ou non)
read_file() {
    local file="$1"
    if [[ "$file" == *.gz ]]; then
        zcat "$file"
    else
        cat "$file"
    fi
}

# Affichage d'un résultat texte
display_result() {
    local entry="$1"
    local ts ip url method status
    ts=$(echo "$entry" | jq -r '.timestamp // "-"')
    ip=$(echo "$entry" | jq -r '.data.source.ip // "-"')
    url=$(echo "$entry" | jq -r '.data.url.original // "-"')
    method=$(echo "$entry" | jq -r '.data.http.request.method // "-"')
    status=$(echo "$entry" | jq -r '.data.http.response.body.status_code // "-"')

    echo "[$ts] $ip  $method  $url  (HTTP $status)"
}

# Formatage d'un résultat CSV
format_csv() {
    local entry="$1"
    local ts ip url method status bytes user_agent
    ts=$(echo "$entry" | jq -r '.timestamp // "-"')
    ip=$(echo "$entry" | jq -r '.data.source.ip // "-"')
    url=$(echo "$entry" | jq -r '.data.url.original // "-"')
    method=$(echo "$entry" | jq -r '.data.http.request.method // "-"')
    status=$(echo "$entry" | jq -r '.data.http.response.body.status_code // "-"')
    bytes=$(echo "$entry" | jq -r '.data.http.response.bytes // "-"')
    user_agent=$(echo "$entry" | jq -r '.data.user_agent.original // "-"')

    # Échapper les guillemets dans l'URL et le user agent
    url=$(echo "$url" | sed 's/"/""/g')
    user_agent=$(echo "$user_agent" | sed 's/"/""/g')

    echo "\"$ts\",\"$ip\",\"$method\",\"$url\",\"$status\",\"$bytes\",\"$user_agent\""
}

# ─── Main ────────────────────────────────────────────────────────────────────

echo ""
echo "🔍 Recherche dans les archives Squid/Wazuh"
[[ -n "$FILTER_IP" ]]  && echo "   IP      : $FILTER_IP"
[[ -n "$FILTER_URL" ]] && echo "   URL     : $FILTER_URL"
[[ -n "$DATE_SPECIFIC" ]] && echo "   Jour    : $DATE_SPECIFIC"
[[ -n "$DATE_FROM" ]]     && echo "   Du      : $DATE_FROM au $DATE_TO"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

RESULTS=0
TMPFILE=$(mktemp)
TMPCSVFILE=$(mktemp)

# En-tête CSV
echo "\"timestamp\",\"ip_source\",\"methode\",\"url\",\"http_status\",\"bytes\",\"user_agent\"" > "$TMPCSVFILE"

while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        match=$(echo "$line" | jq -r "if ($JQ_FILTER) then . else empty end" 2>/dev/null)
        if [[ -n "$match" ]]; then
            display_result "$match" | tee -a "$TMPFILE"
            format_csv "$match" >> "$TMPCSVFILE"
            RESULTS=$((RESULTS + 1))
        fi
    done < <(read_file "$file")
done < <(select_files)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ $RESULTS résultat(s) trouvé(s)."

if [[ -n "$OUTPUT" ]]; then
    cp "$TMPFILE" "$OUTPUT"
    echo "💾 Export texte sauvegardé dans : $OUTPUT"
fi

if [[ -n "$CSV" ]]; then
    cp "$TMPCSVFILE" "$CSV"
    echo "📊 Export CSV sauvegardé dans   : $CSV"
fi

rm -f "$TMPFILE" "$TMPCSVFILE"
