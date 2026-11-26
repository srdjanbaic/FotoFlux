# FotoFlux

**FotoFlux** is a desktop photo editor for Linux, featuring image adjustments, creative filters and AI-powered selective blur.

## Features

### Image Editing
- Brightness, Contrast, Saturation and Sharpness
- Blur and Color Temperature
- Image rotation
- Horizontal and Vertical flipping
- Undo and Reset

### Filters
- 50 built-in image filters
- Live preview
- Original image filter
- Filter search

### AI Selective Blur
- Background Blur – keeps the foreground sharp while blurring the background
- Foreground Blur – blurs the foreground while keeping the background sharp
- Adjustable blur strength
- Local AI processing using the U²-Net model
- CPU-based inference through ONNX Runtime

### Interface
- Scrollable editing controls
- Live image preview
- Simple desktop interface
- Designed for Linux desktop environments

## AI Requirements

FotoFlux uses the `rembg` library and the U²-Net AI model for selective blur.

The AI model is downloaded automatically when first needed and stored locally for subsequent use.

An internet connection is required for the initial model download. After that, AI processing runs locally.

## Installation

Download the latest Debian package (`.deb`) from:

https://github.com/srdjanbaic/FotoFlux/releases

Install it using:

    sudo apt install ./fotoflux_1.0.0_amd64.deb

Launch FotoFlux from your desktop application menu or run:

    fotoflux

## Supported Systems

FotoFlux is intended for 64-bit Debian-based Linux distributions.

The Debian package targets Debian 12 and newer, Ubuntu 22.04 and newer, and compatible distributions.

Compatibility should be verified on each target distribution.

## License

FotoFlux is distributed under the MIT License.
See the LICENSE file for details.

## Maintainer

**FotoFlux Team**

Contact: srdjan.baic@outlook.com

## Project

GitHub: https://github.com/srdjanbaic/FotoFlux
