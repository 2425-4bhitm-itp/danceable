import SwiftUI
import AVFoundation

var recordingQueue = DispatchQueue(label: "recording")

struct ContentView: View {
    @ObservedObject var viewModel: ViewModel
    
    @StateObject private var recorder = AudioRecorder()
    
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    @State var showDancesView = false
    
    @State private var isSheetPresent: Bool = true
    @State private var selectedDetent: PresentationDetent = .fraction(0.125)
    
    @State private var areDancesDisplayed: Bool = false
    
    var body: some View {
        NavigationStack {
            Spacer()
            Button(action: {
                recorder.startRecording(length:5);
            }) {
                ZStack {
                    Circle()
                        .fill(Color(red: 0.48, green: 0.14, blue: 0.58))
                    Image(systemName: "microphone.fill")
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(width: 60)
                        .foregroundStyle(Color.white)
                }
                .padding(75)
                .shadow(radius: 10)
                .sheet(isPresented: $isSheetPresent) {
                    NavigationView {
                        PredictionsView(viewModel: viewModel)
                    }
                    .presentationDetents(
                        [.fraction(0.125), .fraction(0.7), .fraction(1)],
                        selection: $selectedDetent
                    )
                    .presentationBackgroundInteraction(
                        .enabled(upThrough: .fraction(1))
                    )
                    .presentationDragIndicator(.visible)
                    .interactiveDismissDisabled(true)
                }
            }
            Spacer()
            Spacer()
            Spacer()
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    NavigationLink(destination: {
                        DancesView(viewModel: viewModel)
                    }) {
                        Image(systemName: "list.bullet.circle.fill")
                            .resizable()
                            .frame(width: 30, height: 30)
                    }
                }
            }
        }
        .task {
            queue.async(execute: {
                let dances = loadDances()
                
                DispatchQueue.main.async(execute: {
                    viewModel.model.dances = dances
                })
            })
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    return ContentView(viewModel: viewModel)
}
