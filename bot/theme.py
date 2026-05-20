from rich.theme import Theme

# Deep navy-dark fintech palette for the terminal UI
TRADING_THEME = Theme({
    "accent": "#4a9eff",       # Blue accent for headers & prompts
    "value": "#c4b5fd",        # Violet values and tags
    "success": "#34d399",      # Green for success signals
    "buy": "bold #34d399",     # Bold green for BUY tag
    "error": "#f87171",        # Red for error signals
    "sell": "bold #f87171",    # Bold red for SELL tag
    "warning": "#fbbf24",      # Amber for warnings
    "muted": "#94a3b8",        # Muted text for secondary labels
    "dimmed": "#4a506a",       # Dimmed decorative elements / borders
    "surface": "#1a1d27",      # Panel content surface background color
    "border": "#1e2235",       # Panel/Table boundary line color
})
