$docx = "C:\Users\user\Documents\pfe project\Rapport-Stage-CAIDELEC.docx"
$pdf = "C:\Users\user\Documents\pfe project\Rapport-Stage-CAIDELEC.pdf"
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$document = $word.Documents.Open($docx)
$document.SaveAs([ref]$pdf, [ref]17)
$document.Close()
$word.Quit()
Write-Output $pdf
