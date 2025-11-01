# --- Configuration ---
$OUTPUT_FILE = "project-structure.txt"
$SCRIPT_NAME = Split-Path -Leaf $MyInvocation.MyCommand.Path

# Items to exclude
$EXCLUSIONS = @(
    $SCRIPT_NAME,
    $OUTPUT_FILE,
    '__pycache__',
    '.git',
    '.venv',
    'venv',
    'node_modules',
    '.DS_Store',
    '.env',
    '.gitignore',
    'thumbs.db'
)

Write-Host "Generating project structure..."

function Process-Directory {
    param(
        [string]$CurrentDir,
        [string]$ParentPrefix,
        [System.IO.StreamWriter]$FileHandle
    )

    # Get all items in the directory, excluding hidden and excluded items
    try {
        $items = Get-ChildItem -Path $CurrentDir -Force -ErrorAction Stop | 
                 Where-Object { 
                     -not $_.Name.StartsWith('.') -and 
                     $EXCLUSIONS -notcontains $_.Name 
                 } | 
                 Sort-Object Name
    }
    catch {
        Write-Host "Error reading directory ${CurrentDir}: $_"
        return
    }

    # Separate files and directories
    $files = $items | Where-Object { -not $_.PSIsContainer }
    $dirs = $items | Where-Object { $_.PSIsContainer }

    # Combine: files first, then directories
    $sortedItems = @($files) + @($dirs)
    $totalItems = $sortedItems.Count

    for ($i = 0; $i -lt $totalItems; $i++) {
        $item = $sortedItems[$i]
        $isLast = ($i -eq ($totalItems - 1))

        # Determine connector and child prefix
        if ($isLast) {
            $connector = "└── "
            $childPrefix = "    "
        }
        else {
            $connector = "├── "
            $childPrefix = "│   "
        }

        if ($item.PSIsContainer) {
            $FileHandle.WriteLine("${ParentPrefix}${connector}$($item.Name)/")
            # Recursive call for subdirectory
            Process-Directory -CurrentDir $item.FullName -ParentPrefix "${ParentPrefix}${childPrefix}" -FileHandle $FileHandle
        }
        else {
            $FileHandle.WriteLine("${ParentPrefix}${connector}$($item.Name)")
        }
    }
}

# Main execution
try {
    # Create output file with UTF-8 encoding
    $streamWriter = New-Object System.IO.StreamWriter($OUTPUT_FILE, $false, [System.Text.Encoding]::UTF8)
    
    # Write header
    $streamWriter.WriteLine("# Project Directory Structure & Files")
    
    # Get and write root directory name
    $rootDirName = Split-Path -Leaf (Get-Location)
    $streamWriter.WriteLine("${rootDirName}/")
    
    # Start recursive processing
    Process-Directory -CurrentDir "." -ParentPrefix "" -FileHandle $streamWriter
    
    # Close the file
    $streamWriter.Close()
    
    Write-Host "`nProject structure successfully saved to $OUTPUT_FILE"
}
catch {
    Write-Host "Error writing to file ${OUTPUT_FILE}: $_"
}
