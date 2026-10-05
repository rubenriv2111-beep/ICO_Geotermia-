<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories='AllStyleCategories' version='3.44.15' hasScaleBasedVisibilityFlag='0' minScale='1e+08' maxScale='0'>
  <pipe>
    <provider>
      <resampling maxOversampling='2' zoomedOutResamplingMethod='bilinear' zoomedInResamplingMethod='bilinear' enabled='false'/>
    </provider>
    <rasterrenderer alphaBand='-1' classificationMax='125' classificationMin='-625' opacity='1' band='1' type='singlebandpseudocolor'>
      <rasterTransparency>
        <singleValuePixelList>
          <pixelListEntry min='-99999' max='-99999' percentTransparent='100'/>
        </singleValuePixelList>
      </rasterTransparency>
      <rastershader>
        <colorrampshader maximumValue='125' labelPrecision='0' clip='0' colorRampType='DISCRETE' minimumValue='-625'>
          <item alpha='255' value='-600.0' label='< -600 nT (-625 nT)' color='#30123b'/>
          <item alpha='255' value='-550.0' label='-600 a -550 nT' color='#4043a6'/>
          <item alpha='255' value='-500.0' label='-550 a -500 nT' color='#4670e8'/>
          <item alpha='255' value='-450.0' label='-500 a -450 nT' color='#3e9bfe'/>
          <item alpha='255' value='-400.0' label='-450 a -400 nT' color='#21c4e1'/>
          <item alpha='255' value='-350.0' label='-400 a -350 nT' color='#1ae4b6'/>
          <item alpha='255' value='-300.0' label='-350 a -300 nT' color='#46f783'/>
          <item alpha='255' value='-250.0' label='-300 a -250 nT' color='#87fe4d'/>
          <item alpha='255' value='-200.0' label='-250 a -200 nT' color='#b9f534'/>
          <item alpha='255' value='-150.0' label='-200 a -150 nT' color='#e1dc37'/>
          <item alpha='255' value='-100.0' label='-150 a -100 nT' color='#f9ba38'/>
          <item alpha='255' value='-50.0' label='-100 a -50 nT' color='#fd8c27'/>
          <item alpha='255' value='0.0' label='-50 a 0 nT' color='#ef5a11'/>
          <item alpha='255' value='50.0' label='0 a 50 nT' color='#d63405'/>
          <item alpha='255' value='100.0' label='50 a 100 nT' color='#ae1801'/>
          <item alpha='255' value='200.0' label='> 100 nT (+125 nT)' color='#7a0402'/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness='0' contrast='0' gamma='1'/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>