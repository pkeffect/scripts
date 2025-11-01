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

# Statistics tracking
$script:totalFiles = 0
$script:totalDirs = 0
$script:totalSize = 0

function Format-Size {
    param([long]$SizeBytes)
    
    $units = @("B", "KB", "MB", "GB", "TB")
    $unitIndex = 0
    $size = [double]$SizeBytes
    
    while ($size -ge 1024 -and $unitIndex -lt 4) {
        $size = $size / 1024
        $unitIndex++
    }
    
    return "{0:N2} {1}" -f $size, $units[$unitIndex]
}

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

        # Determine connector and child prefix using Unicode characters
        if ($isLast) {
            $connector = [char]0x2514 + [char]0x2500 + [char]0x2500 + " "  # └──
            $childPrefix = "    "
        }
        else {
            $connector = [char]0x251C + [char]0x2500 + [char]0x2500 + " "  # ├──
            $childPrefix = [char]0x2502 + "   "  # │
        }

        if ($item.PSIsContainer) {
            $script:totalDirs++
            $FileHandle.WriteLine("${ParentPrefix}${connector}$($item.Name)/")
            # Recursive call for subdirectory
            Process-Directory -CurrentDir $item.FullName -ParentPrefix "${ParentPrefix}${childPrefix}" -FileHandle $FileHandle
        }
        else {
            $script:totalFiles++
            try {
                $script:totalSize += $item.Length
            }
            catch {
                # Skip if can't get file size
            }
            $FileHandle.WriteLine("${ParentPrefix}${connector}$($item.Name)")
        }
    }
}

# Main execution
try {
    # Create temporary file for tree structure
    $tempFile = "$OUTPUT_FILE.tmp"
    $streamWriter = New-Object System.IO.StreamWriter($tempFile, $false, [System.Text.Encoding]::UTF8)
    
    # Get and write root directory name
    $rootDirName = Split-Path -Leaf (Get-Location)
    $streamWriter.WriteLine("${rootDirName}/")
    
    # Start recursive processing
    Process-Directory -CurrentDir "." -ParentPrefix "" -FileHandle $streamWriter
    
    # Close the temp file
    $streamWriter.Close()
    
    # Read temp file content
    $treeContent = Get-Content -Path $tempFile -Raw -Encoding UTF8
    
    # Write final output with stats at top
    $finalWriter = New-Object System.IO.StreamWriter($OUTPUT_FILE, $false, [System.Text.Encoding]::UTF8)
    $finalWriter.WriteLine("# Project Directory Structure & Files")
    $finalWriter.WriteLine("")
    $finalWriter.WriteLine("# Statistics")
    $finalWriter.WriteLine("Total Directories: $script:totalDirs")
    $finalWriter.WriteLine("Total Files: $script:totalFiles")
    $finalWriter.WriteLine("Total Size: $(Format-Size $script:totalSize)")
    $finalWriter.WriteLine("")
    $finalWriter.Write($treeContent)
    $finalWriter.Close()
    
    # Cleanup temp file
    Remove-Item $tempFile -Force
    
    Write-Host "`nProject structure successfully saved to $OUTPUT_FILE"
    Write-Host "Total Directories: $script:totalDirs"
    Write-Host "Total Files: $script:totalFiles"
    Write-Host "Total Size: $(Format-Size $script:totalSize)"
}
catch {
    Write-Host "Error writing to file ${OUTPUT_FILE}: $_"
}