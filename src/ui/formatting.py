"""Formatting utilities for the Gradio UI."""

from typing import List

from src.config.constants import MAX_LOG_LINES


def html_for(log_data: list[str]) -> str:
    """Generate HTML for displaying the log lines in a scrollable container."""
    logs = reversed(log_data[-MAX_LOG_LINES:])
    output = "".join(f"<div class='log-entry'>{line}</div>" for line in logs)
    return (
        "<div id='logs-label'>📜 Live Agent Logs</div>"
        "<div id='scrollContent'>" + output + "</div>"
    )


def format_deals_table(deals: List[List[str]]) -> str:
    """Formats accepted deals as an HTML table with styled links."""
    html = """
    <div id="deal-table">
        <div id="deals-label">🛍️ Best Deals Found</div>
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Price</th>
                    <th>AI Estimate</th>
                    <th>Discount</th>
                    <th>URL</th>
                </tr>
            </thead>
            <tbody>
    """
    for desc, price, estimate, discount, url in deals:
        html += f"""
                <tr>
                    <td>{desc}</td>
                    <td>{price}</td>
                    <td>{estimate}</td>
                    <td>{discount}</td>
                    <td><a href="{url}" target="_blank">Link</a></td>
                </tr>
        """
    html += """
            </tbody>
        </table>
    </div>
    """
    return html


def get_server_timezone() -> str:
    """Get the server's timezone information."""
    import datetime

    current_time = datetime.datetime.now()
    try:
        timezone_name = current_time.astimezone().tzinfo.tzname(current_time)
    except AttributeError:
        timezone_name = "Unknown"

    return (
        f"Server Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} "
        f"(Timezone: {timezone_name})"
    )
