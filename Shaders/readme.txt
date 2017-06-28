					Mount&Blade Warband Shaders

mb.fx:
- You can add edit main shaders and lighting system with this file. 
- Use compile_fx.bat to compile fxo files. (mb_2a.fxo and mb_2b.fxo)

postfx.fx:
- This file is used for HDR and DoF effects. You cannot modify postFX pipeline
  and render targets but apply changes to generate different tonemappings or effects.
- This file is compiled on-demand according to selected module_postfx parameters.


- We don't give you the source codes for earlyz.fxo since its not directly related 
with the lighting or shading and contains hardcoded depth rendering.
- Do not change fx_configuration.h file since it holds application dependent 
configration parameters. 

Please send your feedbacks to our forums or PM me(Serdar). 

						All rights reserved.
						 www.taleworlds.com
