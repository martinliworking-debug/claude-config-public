# =====================================================================
# commit-reminder.ps1  -  Claude Code "Stop" hook
#
# Nudge only. It NEVER commits, NEVER blocks, and ALWAYS exits 0.
# If the cwd is inside a git repo with uncommitted changes, it emits a
# JSON systemMessage reminding you to commit the source layer and update
# _project/STATUS.md. Otherwise it is silent.
#
# PowerShell 5.1 note: never pipe a native exe's stderr with 2>&1 - it
# wraps each stderr line in an ErrorRecord and trips
# $ErrorActionPreference='Stop' even when the exe returns 0.
# =====================================================================

$ErrorActionPreference = 'SilentlyContinue'

try {
    $dir = (Get-Location).Path

    # Walk up looking for .git, so we never invoke git outside a repo.
    $probe = $dir
    $repo  = $null
    while ($probe) {
        if (Test-Path -LiteralPath (Join-Path $probe '.git')) { $repo = $probe; break }
        $parent = Split-Path -Parent $probe
        if (-not $parent -or $parent -eq $probe) { break }
        $probe = $parent
    }
    if (-not $repo) { exit 0 }

    Push-Location -LiteralPath $repo
    $raw = git status --porcelain
    Pop-Location

    $changes = @($raw | Where-Object { $_ -and $_.Trim() -ne '' })
    if ($changes.Count -eq 0) { exit 0 }

    $name = Split-Path -Leaf $repo
    if ($changes.Count -eq 1) { $noun = 'change' } else { $noun = 'changes' }

    $msg = "$($changes.Count) uncommitted $noun in $name. Commit the source layer and update _project/STATUS.md before you close out."

    $payload = @{ systemMessage = $msg } | ConvertTo-Json -Compress
    Write-Output $payload
}
catch {
    # Swallow everything. A reminder must never interfere with the session ending.
}

exit 0
