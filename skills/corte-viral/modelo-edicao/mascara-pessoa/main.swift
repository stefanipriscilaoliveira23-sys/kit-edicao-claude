// Gera um vídeo de máscara (branco = pessoa, preto = fundo) usando o recorte de pessoas do macOS (Vision).
// Uso: mascara-pessoa <entrada.mp4> <saida-mascara.mp4> [largura=540]
// A máscara depois entra no ffmpeg para desfocar só o fundo (modo retrato).
import AVFoundation
import CoreImage
import Vision

let args = CommandLine.arguments
guard args.count >= 3 else { print("uso: mascara-pessoa entrada.mp4 saida.mp4 [largura]"); exit(1) }
let entrada = URL(fileURLWithPath: args[1]), saida = URL(fileURLWithPath: args[2])
let largura = args.count > 3 ? Int(args[3]) ?? 540 : 540

let asset = AVURLAsset(url: entrada)
let sem = DispatchSemaphore(value: 0)
var faixa: AVAssetTrack?
Task { faixa = try? await asset.loadTracks(withMediaType: .video).first; sem.signal() }
sem.wait()
guard let video = faixa else { print("sem trilha de video"); exit(1) }
var tamanho = CGSize.zero, transform = CGAffineTransform.identity, fps: Float = 30
Task {
    tamanho = (try? await video.load(.naturalSize)) ?? .zero
    transform = (try? await video.load(.preferredTransform)) ?? .identity
    fps = (try? await video.load(.nominalFrameRate)) ?? 30
    sem.signal()
}
sem.wait()
let girado = tamanho.applying(transform)
let W = largura, H = Int((Double(largura) * abs(girado.height) / abs(girado.width)).rounded() / 2) * 2

let leitor = try AVAssetReader(asset: asset)
let saidaLeitor = AVAssetReaderTrackOutput(track: video, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
saidaLeitor.alwaysCopiesSampleData = false
leitor.add(saidaLeitor)
leitor.startReading()

try? FileManager.default.removeItem(at: saida)
let escritor = try AVAssetWriter(outputURL: saida, fileType: .mp4)
let entradaEscritor = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264, AVVideoWidthKey: W, AVVideoHeightKey: H,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 4_000_000]])
let adaptador = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: entradaEscritor, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA, kCVPixelBufferWidthKey as String: W, kCVPixelBufferHeightKey as String: H])
escritor.add(entradaEscritor)
escritor.startWriting()
escritor.startSession(atSourceTime: .zero)

let ci = CIContext()
let pedido = VNGeneratePersonSegmentationRequest()
pedido.qualityLevel = .balanced
pedido.outputPixelFormat = kCVPixelFormatType_OneComponent8
// orientação da gravação do iPhone (vídeo em pé gravado com rotação)
let angulo = atan2(transform.b, transform.a)
let orient: CGImagePropertyOrientation = abs(angulo - .pi/2) < 0.1 ? .right : (abs(angulo + .pi/2) < 0.1 ? .left : (abs(abs(angulo) - .pi) < 0.1 ? .down : .up))
var n = 0
while let amostra = saidaLeitor.copyNextSampleBuffer() {
    guard let pb = CMSampleBufferGetImageBuffer(amostra) else { continue }
    let t = CMSampleBufferGetPresentationTimeStamp(amostra)
    let h = VNImageRequestHandler(cvPixelBuffer: pb, orientation: orient)
    try? h.perform([pedido])
    guard let m = pedido.results?.first?.pixelBuffer else { continue }
    var img = CIImage(cvPixelBuffer: m)
    // a máscara vem num canal só: copia pro RGB pra virar cinza (branco = pessoa)
    let r = CIVector(x: 1, y: 0, z: 0, w: 0)
    img = img.applyingFilter("CIColorMatrix", parameters: ["inputRVector": r, "inputGVector": r, "inputBVector": r, "inputAVector": CIVector(x: 0, y: 0, z: 0, w: 1)])
    img = img.transformed(by: CGAffineTransform(scaleX: CGFloat(W) / img.extent.width, y: CGFloat(H) / img.extent.height))
    while !entradaEscritor.isReadyForMoreMediaData { usleep(2000) }
    var out: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptador.pixelBufferPool!, &out)
    if let out = out {
        ci.render(img, to: out)
        adaptador.append(out, withPresentationTime: t)
    }
    n += 1
    if n % 300 == 0 { print("quadros: \(n)"); fflush(stdout) }
}
entradaEscritor.markAsFinished()
escritor.finishWriting { sem.signal() }
sem.wait()
print("ok \(n) quadros \(W)x\(H) -> \(saida.path)")
