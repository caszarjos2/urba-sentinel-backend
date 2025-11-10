"""
Utilidades para trabajar con FFmpeg: cortar y concatenar clips sin recodificar.
"""
import asyncio
import os
from typing import List
from pathlib import Path

from app.config.settings import settings


async def cut_part(
    src: str,
    ss: float,
    dur: float,
    out_tmp: str
) -> bool:
    """
    Corta una parte de un video sin recodificar.
    
    Args:
        src: Ruta del video fuente
        ss: Segundo de inicio
        dur: Duración en segundos
        out_tmp: Ruta del archivo de salida
    
    Returns:
        True si fue exitoso
    """
    cmd = [
        settings.FFMPEG_PATH,
        "-ss", str(ss),
        "-i", src,
        "-t", str(dur),
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        "-y",
        out_tmp
    ]
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return True
        else:
            print(f"Error cortando video: {stderr.decode()}")
            return False
    except Exception as e:
        print(f"Excepción al cortar video: {e}")
        return False


async def concat_videos(
    parts_tmp: List[str],
    out_path: str,
    fallback_encode: bool = True
) -> bool:
    """
    Concatena múltiples videos sin recodificar usando demuxer concat.
    Si falla, intenta con recodificación (fallback).
    
    Args:
        parts_tmp: Lista de rutas a videos temporales
        out_path: Ruta del video final concatenado
        fallback_encode: Si es True y falla concat, intenta recodificar
    
    Returns:
        True si fue exitoso
    """
    # Crear archivo de lista para concat demuxer
    concat_file = out_path + ".concat.txt"
    
    try:
        with open(concat_file, "w") as f:
            for part in parts_tmp:
                # Escapar ruta para FFmpeg
                escaped = part.replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{escaped}'\n")
        
        # Intentar concat sin recodificar
        cmd = [
            settings.FFMPEG_PATH,
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-y",
            out_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return True
        
        # Si falló y hay fallback, intentar con recodificación
        if fallback_encode:
            print("Concat sin recodificar falló, intentando con recodificación...")
            cmd_encode = [
                settings.FFMPEG_PATH,
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c:v", "libx264",
                "-preset", "fast",
                "-c:a", "aac",
                "-movflags", "+faststart",
                "-y",
                out_path
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd_encode,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            return process.returncode == 0
        
        return False
        
    except Exception as e:
        print(f"Excepción al concatenar videos: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists(concat_file):
            os.remove(concat_file)


async def cut_and_concat(
    clips: List[tuple],
    out_path: str,
    temp_dir: str
) -> bool:
    """
    Corta partes de múltiples clips y las concatena en un solo video.
    
    Args:
        clips: Lista de tuplas (storage_path, ss, dur)
        out_path: Ruta del video final
        temp_dir: Directorio temporal para archivos intermedios
    
    Returns:
        True si fue exitoso
    """
    Path(temp_dir).mkdir(parents=True, exist_ok=True)
    parts_tmp = []
    
    try:
        # Cortar cada parte
        for i, (storage_path, ss, dur) in enumerate(clips):
            tmp_path = os.path.join(temp_dir, f"part_{i}.mp4")
            success = await cut_part(storage_path, ss, dur, tmp_path)
            
            if not success:
                print(f"Error cortando parte {i}")
                return False
            
            parts_tmp.append(tmp_path)
        
        # Si solo hay una parte, mover directamente
        if len(parts_tmp) == 1:
            os.rename(parts_tmp[0], out_path)
            return True
        
        # Concatenar todas las partes
        success = await concat_videos(parts_tmp, out_path)
        return success
        
    finally:
        # Limpiar archivos temporales
        for tmp in parts_tmp:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except Exception:
                    pass