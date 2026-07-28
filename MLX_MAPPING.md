## MiniLibX / pygame function mapping

This project uses `pygame` as a graphical library. Per the subject constraint
("A graphical library is considered *similar to MLX* if each function you use
has an equivalent in the MLX library"), the table below lists every pygame
function used in this project and its conceptual MiniLibX equivalent.

| MiniLibX function | pygame equivalent | Purpose |
|---|---|---|
| `mlx_init()` | `pygame.init()` | Initialize the connection / library |
| `mlx_new_window(mlx_ptr, size_x, size_y, title)` | `pygame.display.set_mode((w, h))` + `pygame.display.set_caption(title)` | Create the window |
| `mlx_clear_window(mlx_ptr, win_ptr)` | `screen.fill((0, 0, 0))` | Clear the window (black) |
| `mlx_destroy_window(mlx_ptr, win_ptr)` | `pygame.display.quit()` / `pygame.quit()` | Destroy the window |
| `mlx_new_image(mlx_ptr, width, height)` | `pygame.Surface((w, h), pygame.SRCALPHA)` | Create a blank image in memory |
| `mlx_get_data_addr(img_ptr, &bpp, &size_line, &endian)` | `pygame.PixelArray(surface)` / `pygame.surfarray.pixels3d(surface)` | Direct pixel buffer access |
| `mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, x, y)` | `screen.blit(image, (x, y))` | Draw an image into the window |
| `mlx_get_color_value(mlx_ptr, color)` | RGB tuple `(r, g, b)` used directly | Color encoding |
| `mlx_xpm_to_image(mlx_ptr, xpm_data, &w, &h)` | `pygame.image.load(io.BytesIO(data))` | Load an image from in-memory data |
| `mlx_xpm_file_to_image(mlx_ptr, filename, &w, &h)` | `pygame.image.load(filename)` | Load an image from a file |
| `mlx_destroy_image(mlx_ptr, img_ptr)` | *(no strict equivalent — Python garbage-collects the Surface)* | Free image memory |
| `mlx_pixel_put(mlx_ptr, win_ptr, x, y, color)` | `screen.set_at((x, y), color)` | Draw a single pixel |
| `mlx_string_put(mlx_ptr, win_ptr, x, y, color, string)` | `font.render(string, True, color)` then `screen.blit(text_surface, (x, y))` | Draw text |
| `mlx_loop(mlx_ptr)` | `while running: ...` | Main event loop |
| `mlx_key_hook(win_ptr, funct_ptr, param)` | `for event in pygame.event.get(): if event.type == pygame.KEYDOWN` | Key press callback |
| `mlx_mouse_hook(win_ptr, funct_ptr, param)` | `for event in pygame.event.get(): if event.type == pygame.MOUSEBUTTONDOWN` | Mouse click callback |
| `mlx_expose_hook(win_ptr, funct_ptr, param)` | *(not required — pygame redraws the whole frame every loop iteration)* | Window redraw callback |
| `mlx_loop_hook(mlx_ptr, funct_ptr, param)` | Body of the `while running:` loop, executed every iteration before `pygame.display.flip()` | Idle callback |
| `mlx_hook(win_ptr, event, mask, funct_ptr, param)` | `pygame.event.get()` (generic access to all events) | Low-level generic event hook |
| *(no direct MLX equivalent — manual buffer offset in C)* | `Surface.subsurface(rect)` | Crop a single sprite out of a spritesheet by extracting a sub-region view of an already-loaded image buffer, equivalent to a manual offset into the buffer returned by `mlx_get_data_addr()` in C |
| `mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, x, y)` | `screen.blit(image, (x, y), area)` | Draw only a sub-region (`area`) of a source image into the window — same call as above, with an extra parameter restricting the copied zone |

### Notes

- **Text centering**: `Surface.get_rect(center=...)` and `Surface.get_width()`
  have no direct MLX equivalent, but they only compute coordinates — they draw
  nothing. The actual drawing call remains `blit()`, the equivalent of
  `mlx_put_image_to_window` / `mlx_string_put`.
- **FPS handling**: `pygame.time.Clock().tick(fps)` was deliberately **not**
  used, since it has no MLX equivalent (MLX has no built-in FPS limiter — this
  would be handled manually in a `loop_hook` in C). Instead, FPS limiting is
  reimplemented manually using `time.perf_counter()` and `time.sleep()`,
  standard OS-level primitives equivalent to what a C developer would use
  (e.g. `gettimeofday()` / `usleep()`).
- **Image formats**: MLX only natively supports XPM. `pygame.image.load()`
  supports more formats (PNG, JPG, BMP, GIF...) — a functional superset of
  `mlx_xpm_file_to_image()`, used here for convenience while keeping the same
  conceptual role (load an image file into memory).