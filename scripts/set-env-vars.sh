SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)

export CLOSED_AUCTION_METRICS_DIR_PATH="$(dirname "$SCRIPT_DIR")"

result="${CLOSED_AUCTION_METRICS_DIR_PATH%"${CLOSED_AUCTION_METRICS_DIR_PATH##*[!/]}"}" # extglob-free multi-trailing-/ trim
result="${result##*/}"                                    # remove everything before the last /
result=${result:-/}                             # correct for dirname=/ case

export CLOSED_AUCTION_METRICS_DIR_NAME=$result

echo
echo "SETTING ENVIRONMENT VARIABLES (closed-auction-metrics)..."
echo CLOSED_AUCTION_METRICS_DIR_PATH=$CLOSED_AUCTION_METRICS_DIR_PATH
echo CLOSED_AUCTION_METRICS_DIR_NAME=$result
echo

