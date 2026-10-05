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
        <colorrampshader maximumValue='125' labelPrecision='0' clip='0' colorRampType='INTERPOLATED' minimumValue='-625'>
          <item alpha='255' value='-625.0' label='-625 nT (Bajo Extremo)' color='#30123b'/>
          <item alpha='255' value='-575.0' label='-550 nT' color='#4043a6'/>
          <item alpha='255' value='-525.0' label='-500 nT' color='#4670e8'/>
          <item alpha='255' value='-475.0' label='-450 nT' color='#3e9bfe'/>
          <item alpha='255' value='-425.0' label='-400 nT' color='#21c4e1'/>
          <item alpha='255' value='-375.0' label='-350 nT' color='#1ae4b6'/>
          <item alpha='255' value='-325.0' label='-300 nT' color='#46f783'/>
          <item alpha='255' value='-275.0' label='-250 nT' color='#87fe4d'/>
          <item alpha='255' value='-225.0' label='-200 nT' color='#b9f534'/>
          <item alpha='255' value='-175.0' label='-150 nT' color='#e1dc37'/>
          <item alpha='255' value='-125.0' label='-100 nT' color='#f9ba38'/>
          <item alpha='255' value='-75.0' label='-50 nT' color='#fd8c27'/>
          <item alpha='255' value='-25.0' label='0 nT' color='#ef5a11'/>
          <item alpha='255' value='25.0' label='+50 nT' color='#d63405'/>
          <item alpha='255' value='75.0' label='+100 nT' color='#ae1801'/>
          <item alpha='255' value='125.0' label='+125 nT (Alto Extremo)' color='#7a0402'/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness='0' contrast='0' gamma='1'/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>