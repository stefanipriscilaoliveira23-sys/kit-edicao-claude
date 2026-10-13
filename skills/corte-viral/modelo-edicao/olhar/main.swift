// Mede para onde o rosto está virado em cada quadro (Vision do macOS).
// Saída CSV: tempo,yaw,pitch,tem_rosto,cx,cy,larg   (yaw/pitch em graus; cx/cy = centro do rosto em fração do quadro, y a partir do topo)
// Uso: olhar <video> <saida.csv> [pular=2]   (analisa 1 a cada N quadros)
import AVFoundation
import Vision

let a = CommandLine.arguments
guard a.count >= 3 else { print("uso: olhar video saida.csv [pular]"); exit(1) }
let asset = AVURLAsset(url: URL(fileURLWithPath: a[1]))
let pular = a.count > 3 ? Int(a[3]) ?? 2 : 2
let sem = DispatchSemaphore(value: 0)
var faixa: AVAssetTrack?; var tr = CGAffineTransform.identity
Task { faixa = try? await asset.loadTracks(withMediaType: .video).first; if let f = faixa { tr = (try? await f.load(.preferredTransform)) ?? .identity }; sem.signal() }
sem.wait()
guard let video = faixa else { exit(1) }
let ang = atan2(tr.b, tr.a)
let orient: CGImagePropertyOrientation = abs(ang - .pi/2) < 0.1 ? .right : (abs(ang + .pi/2) < 0.1 ? .left : (abs(abs(ang) - .pi) < 0.1 ? .down : .up))
let leitor = try AVAssetReader(asset: asset)
let out = AVAssetReaderTrackOutput(track: video, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_420YpCbCr8BiPlanarFullRange])
out.alwaysCopiesSampleData = false
leitor.add(out); leitor.startReading()
var linhas = ["tempo,yaw,pitch,tem_rosto,cx,cy,larg"]; var i = 0
let pedido = VNDetectFaceRectanglesRequest()
pedido.revision = VNDetectFaceRectanglesRequestRevision3
while let s = out.copyNextSampleBuffer() {
    i += 1
    if i % pular != 0 { continue }
    guard let pb = CMSampleBufferGetImageBuffer(s) else { continue }
    let t = CMTimeGetSeconds(CMSampleBufferGetPresentationTimeStamp(s))
    try? VNImageRequestHandler(cvPixelBuffer: pb, orientation: orient).perform([pedido])
    // maior rosto do quadro
    if let f = pedido.results?.max(by: { $0.boundingBox.width < $1.boundingBox.width }) {
        let yaw = (f.yaw?.doubleValue ?? 0) * 180 / .pi, pitch = (f.pitch?.doubleValue ?? 0) * 180 / .pi
        let b = f.boundingBox
        linhas.append(String(format: "%.3f,%.1f,%.1f,1,%.3f,%.3f,%.3f", t, yaw, pitch, b.midX, 1 - b.midY, b.width))
    } else {
        linhas.append(String(format: "%.3f,0,0,0,0,0,0", t))
    }
}
try linhas.joined(separator: "\n").write(toFile: a[2], atomically: true, encoding: .utf8)
print("ok \(linhas.count - 1) quadros analisados")
