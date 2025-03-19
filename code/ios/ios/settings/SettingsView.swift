import SwiftUI

struct SettingsView: View {
    let queue = DispatchQueue(label: "at.htl.leonding")
    
    @ObservedObject var viewModel: ViewModel
    
    var body: some View {
        HStack {
            Text("gearshape.fill")
                .font(.title)
                .padding(.leading)
            Spacer()
        }
        Spacer()
        VStack {
            List ($viewModel.danceSettings) { $danceSetting in
                HStack {
                    Text(danceSetting.dance.name)
                    
                    Toggle("", isOn: $danceSetting.isActive)
                                .toggleStyle(SwitchToggleStyle())
                }
            }
        }.task {
            queue.async(execute: {
                let dances = loadDanceSettings()
                DispatchQueue.main.async(execute: {
                    viewModel.model.danceSettings = dances
                })
            })
        }
    }
}

#Preview {
    let model: Model = Model()
    let viewModel: ViewModel = ViewModel(model: model)
    
    let settingsView = SettingsView(viewModel: viewModel)
    return settingsView
}
