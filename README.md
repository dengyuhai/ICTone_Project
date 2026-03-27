# ICTone Project Page

Project page and assets for:

**Towards In-Context Tone Style Transfer with A Large-Scale Triplet Dataset**

## Overview

This repository hosts the academic project page for **ICTone**, a diffusion-based framework for semantic-aware tone style transfer, together with the accompanying paper assets.

The project introduces:

- **TST100K**: the first large-scale dataset of 100,000 content-reference-stylized triplets for tone style transfer
- **TST2K**: a curated benchmark for evaluation across diverse real-world scenarios
- **Tone Style Scorer**: a two-stage similarity model used for triplet filtering and reward feedback learning
- **ICTone**: an in-context diffusion framework that jointly conditions on content and reference images

## Repository Structure

- `index.html`: project page
- `static/`: CSS, JavaScript, and paper PDF assets

## Paper

The paper PDF is available at:

- `static/pdfs/ICTone_paper.pdf`

## Project Page

Open `index.html` locally or deploy this repository with GitHub Pages. The page only depends on files under `static/`, so it can be published without the local LaTeX source folder.

## Citation

```bibtex
@article{deng2026ictone,
  title={Towards In-Context Tone Style Transfer with A Large-Scale Triplet Dataset},
  author={Deng, Yuhai and She, Huimin and Shen, Wei and Li, Meng and Wu, Ruoxi and Yuan, Lunxi and Li, Xiang},
  journal={Under Review},
  year={2026},
  url={https://github.com/dengyuhai/ICTone_Project}
}
```
