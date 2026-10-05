<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories='AllStyleCategories' version='3.44.15' hasScaleBasedVisibilityFlag='0' minScale='1e+08' maxScale='0'>
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <customproperties/>
  <pipe-data-defined-properties>
    <Option type='Map'>
      <Option value='' name='name' type='QString'/>
      <Option name='properties'/>
      <Option value='collection' name='type' type='QString'/>
    </Option>
  </pipe-data-defined-properties>
  <pipe>
    <provider>
      <resampling maxOversampling='2' zoomedOutResamplingMethod='bilinear' zoomedInResamplingMethod='bilinear' enabled='false'/>
    </provider>
    <rasterrenderer alphaBand='-1' classificationMax='150' classificationMin='-550' opacity='1' nodataColor='' band='1' type='singlebandpseudocolor'>
      <rasterTransparency>
        <singleValuePixelList>
          <pixelListEntry min='-99999' max='-99999' percentTransparent='100'/>
        </singleValuePixelList>
      </rasterTransparency>
      <minMaxOrigin>
        <limits>None</limits>
        <extent>WholeRaster</extent>
        <statAccuracy>Estimated</statAccuracy>
        <cumulativeCutLower>0.02</cumulativeCutLower>
        <cumulativeCutUpper>0.98</cumulativeCutUpper>
        <stdDevFactor>2</stdDevFactor>
      </minMaxOrigin>
      <rastershader>
        <colorrampshader maximumValue='150' labelPrecision='0' clip='0' colorRampType='INTERPOLATED' minimumValue='-550' classificationMode='1'>
          <item alpha='255' value='-550' label='-550 nT (Bajo Extremo)' color='#04b4e6'/>
          <item alpha='255' value='-500' label='-500 nT' color='#5ac4ea'/>
          <item alpha='255' value='-450' label='-450 nT' color='#82cfeb'/>
          <item alpha='255' value='-400' label='-400 nT' color='#a6d7e2'/>
          <item alpha='255' value='-350' label='-350 nT' color='#cbe8dd'/>
          <item alpha='255' value='-300' label='-300 nT' color='#dfefde'/>
          <item alpha='255' value='-250' label='-250 nT' color='#e3f2e7'/>
          <item alpha='255' value='-200' label='-200 nT' color='#f0f7e7'/>
          <item alpha='255' value='-150' label='-150 nT' color='#fffcdf'/>
          <item alpha='255' value='-100' label='-100 nT' color='#fffbd2'/>
          <item alpha='255' value='-50'  label='-50 nT'  color='#ffeebc'/>
          <item alpha='255' value='0'    label='0 nT'    color='#ffe4b8'/>
          <item alpha='255' value='50'   label='50 nT'   color='#fdd1b0'/>
          <item alpha='255' value='100'  label='100 nT'  color='#faad7c'/>
          <item alpha='255' value='125'  label='125 nT'  color='#f89b5c'/>
          <item alpha='255' value='150'  label='150 nT (Alto Magnético)' color='#f58345'/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness='0' contrast='0' gamma='1'/>
    <huesaturation colorizeBlue='128' colorizeRed='255' colorizeOn='0' grayscaleMode='0' colorizeStrength='100' colorizeGreen='128' saturation='0' invertColors='0'/>
    <rasterresampler maxOversampling='2'/>
    <resamplingStage>resamplingFilter</resamplingStage>
  </pipe>
  <blendMode>0</blendMode>
</qgis>
