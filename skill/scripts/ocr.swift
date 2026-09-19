import Foundation
import PDFKit
import Vision

// 用法: swift ocr.swift <input.pdf> <output.md> [起始页] [结束页]
// PDFKit 渲染 300dpi + Vision 中文识别，流式写出，每页标 [OCR·p N]

let args = CommandLine.arguments
guard args.count >= 3 else {
    print("usage: ocr.swift <input.pdf> <output.md> [startPage] [endPage]")
    exit(1)
}
let url = URL(fileURLWithPath: args[1])
let outURL = URL(fileURLWithPath: args[2])
let startPage = args.count > 3 ? Int(args[3]) ?? 1 : 1
let endPageArg = args.count > 4 ? Int(args[4]) : nil

guard let doc = PDFDocument(url: url) else {
    print("cannot open pdf")
    exit(1)
}
let total = doc.pageCount
let endPage = min(endPageArg ?? total, total)
let scale: CGFloat = 300.0 / 72.0

FileManager.default.createFile(atPath: outURL.path, contents: nil)
let handle = try FileHandle(forWritingTo: outURL)

var recognizedChars = 0

for pageNum in startPage...endPage {
    guard let page = doc.page(at: pageNum - 1) else { continue }
    let bounds = page.bounds(for: .mediaBox)
    let w = Int(bounds.width * scale)
    let h = Int(bounds.height * scale)

    let colorSpace = CGColorSpaceCreateDeviceRGB()
    guard let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8,
                              bytesPerRow: 0, space: colorSpace,
                              bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { continue }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1))
    ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale)
    ctx.translateBy(x: bounds.origin.x, y: bounds.origin.y)
    page.draw(with: .mediaBox, to: ctx)
    guard let cgImage = ctx.makeImage() else { continue }

    let request = VNRecognizeTextRequest { _, _ in }
    request.recognitionLevel = .accurate
    request.recognitionLanguages = ["zh-Hans", "en-US"]
    request.usesLanguageCorrection = true

    let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
    try? handler.perform([request])

    var text = ""
    if let observations = request.results {
        text = observations.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n")
    }
    recognizedChars += text.count
    let out = "\n\n[OCR·p \(pageNum)]\n\n\(text)"
    try? handle.write(contentsOf: out.data(using: .utf8)!)
    if pageNum % 10 == 0 {
        print("page \(pageNum)/\(endPage), chars so far \(recognizedChars)")
        try? handle.synchronize()
    }
}
handle.closeFile()
print("DONE pages \(startPage)-\(endPage), total chars \(recognizedChars)")
