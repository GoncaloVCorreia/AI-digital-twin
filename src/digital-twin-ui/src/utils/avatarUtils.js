/**
 * Automatically detect available avatars in the /public/avatars folder
 * Scans for Avatar_1.png, Avatar_2.png, etc.
 * @returns {Promise<string[]>} Array of avatar names (e.g., ["Avatar_1", "Avatar_2"])
 */
export async function detectAvailableAvatars() {
  const detectedAvatars = [];
  let index = 1;
  let consecutiveFails = 0;
  const maxConsecutiveFails = 3;

  while (consecutiveFails < maxConsecutiveFails) {
    const avatarName = `Avatar_${index}`;
    const avatarPath = `/avatars/${avatarName}.png`;
    
    try {
      const exists = await checkImageExists(avatarPath);
      if (exists) {
        detectedAvatars.push(avatarName);
        consecutiveFails = 0;
      } else {
        consecutiveFails++;
      }
    } catch {
      consecutiveFails++;
    }
    
    index++;
    
    if (index > 100) break; // Safety limit
  }

  console.log(`Detected ${detectedAvatars.length} avatars:`, detectedAvatars);
  return detectedAvatars.length > 0 ? detectedAvatars : ["default"];
}

/**
 * Check if an image exists at the given URL
 * @param {string} url - Image URL to check
 * @returns {Promise<boolean>}
 */
export function checkImageExists(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = url;
  });
}

/**
 * Get the full avatar path for a persona
 * @param {object} persona - Persona object with optional avatar property
 * @returns {string} Full path to avatar image
 */
export function getAvatarUrl(persona) {
  if (persona && persona.avatar) {
    return `/avatars/${persona.avatar}.png`;
  }
  if (persona && persona.name) {
    return `/avatars/${persona.name.toLowerCase()}.png`;
  }
  return '/avatars/default.png';
}
