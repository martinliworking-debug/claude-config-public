# Claude Code Account Switcher (credentials-only)
# Usage: switch-account.ps1
#
# Clears the cached login so the next `claude` start prompts for authentication,
# letting you sign in as a different account. Config does not switch with the
# account: it is credentials-only.

$claudeDir = "$env:USERPROFILE\.claude"
$creds = "$claudeDir\.credentials.json"

if (Test-Path $creds) {
    Remove-Item $creds -Confirm:$false
    Write-Host "Credentials cleared." -ForegroundColor Green
} else {
    Write-Host "No cached credentials found (already logged out)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Run 'claude login' (or just start claude) to sign in as the other account." -ForegroundColor Green
