# Sample Piper voice

The scaffold script can copy a sample Piper voice into generated projects if the model files are present here:

- `en_US-lessac-medium.onnx`
- `en_US-lessac-medium.onnx.json`

The voice can also be downloaded into a generated project with:

```bash
./devenv.sh 'python -m piper.download_voices en_US-lessac-medium --data-dir voices'
```

Before publishing, verify the upstream Piper voice/model license and disclose synthesized narration where appropriate.
