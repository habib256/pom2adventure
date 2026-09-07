/* paths.h - Path management API for ProDOS directory structure */
#ifndef PATHS_H
#define PATHS_H

/* Build paths for a scene number (0-999)
 * Returns 0 on success, -1 if scene_id out of range
 * Paths use ProDOS relative path format (no leading slash):
 *   imgPath: DHGR/N<id>.RLE
 *   txtPath: TEXTFR/N<subdirectory>/N<id>.TXT or TEXTEN/N<subdirectory>/N<id>.TXT
 *   subdirectory is calculated as (scene_id / 50) * 50 (N000, N050, N100, etc.)
 * Example: scene_id=1, lang="FR" -> 
 *   imgPath: "DHGR/N001.RLE"
 *   txtPath: "TEXTFR/N000/N001.TXT"
 */
char* put_scene(char* p, unsigned int id);
int build_paths(unsigned int scene_id, const char* lang, 
                char* imgPath, char* txtPath);

#endif /* PATHS_H */
