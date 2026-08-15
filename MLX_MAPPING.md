## MiniLibX / pygame function mapping

The project uses only Pygame operations that have a MiniLibX equivalent or
perform ordinary coordinate calculations. Sprite cropping, resizing, walls,
circles, and pacgums are implemented pixel by pixel instead of relying on
higher-level Pygame drawing or transform helpers.

| MiniLibX function or mechanism | Pygame equivalent used | Purpose |
| --- | --- | --- |
| `mlx_init()` | `pygame.init()` and `pygame.font.init()` | Initialize the graphical services |
| `mlx_new_window()` | `pygame.display.set_mode()` and `pygame.display.set_caption()` | Create the centered window scaled from the 1000×1500 reference |
| `mlx_clear_window()` | `Surface.fill()` | Clear the current frame |
| `mlx_destroy_window()` | `pygame.quit()` | Release the graphical resources |
| `mlx_new_image()` | `pygame.Surface()` | Create an image buffer |
| `mlx_get_data_addr()` / buffer access | `Surface.get_at()` and `Surface.set_at()` | Read and write individual pixels |
| `mlx_put_image_to_window()` | `Surface.blit()` | Copy an image to the window |
| `mlx_pixel_put()` | `Surface.set_at()` | Draw walls, circles, dots, and resized sprites pixel by pixel |
| `mlx_xpm_file_to_image()` | `pygame.image.load()` | Load the supplied sprite sheet |
| `mlx_string_put()` | `pygame.font.Font().render()` followed by `Surface.blit()` | Draw the bundled game font |
| `mlx_loop()` / expose refresh | Main `while` loops and `pygame.display.flip()` | Process and present frames |
| `mlx_key_hook()` | `pygame.event.get()` with `KEYDOWN` and key constants | Read menu, movement, pause, and cheat keys |
| `mlx_hook()` for window close | `pygame.event.get()` with `QUIT` | Close from every active page or modal |
| Manual frame timing in a loop hook | `SimpleClock` using `time.perf_counter()` and `time.sleep()` | Limit the game to 60 FPS |

Geometry helpers such as `Surface.get_size()`, `get_width()`, `get_height()`,
and `get_rect(center=...)` only calculate sizes or coordinates. They do not add
a graphical primitive beyond the image and text operations mapped above.

`SpritesChunker` copies sprite-sheet pixels into a new `Surface`; it does not
use `Surface.subsurface()`. `DrawTools.resize_surface()` performs nearest-
neighbor scaling with `get_at()` and `set_at()` and does not use
`pygame.transform.scale()`.

Pygame loads the supplied PNG sprite sheet, whereas classic MiniLibX loads XPM
files. Both calls have the same project role: decoding one bundled image into
an image buffer before the loop starts.
