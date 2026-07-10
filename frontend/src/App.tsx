import './App.css';
import Chat from './components/Chat';
import Navbar from './components/Navbar';
import Upload from './components/Upload';

function App() {
  return (
    <div>
      <Navbar />
      <Upload />
      <Chat />
    </div>
  );
}

export default App;
