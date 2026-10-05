https://github.com/KennethJAllen/proper-pixel-art
wrapper node

WIP

note

- Security: input_path and intermediate_dir accept arbitrary server paths; use only with trusted workflow users.
- Input paths refer to the machine running ComfyUI.
- Avoid output directory names containing a dot; it may fail. (upstream specification)
