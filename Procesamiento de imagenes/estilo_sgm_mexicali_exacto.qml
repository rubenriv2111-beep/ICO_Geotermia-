<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories='AllStyleCategories' version='3.44.15' hasScaleBasedVisibilityFlag='0' minScale='1e+08' maxScale='0'>
  <pipe>
    <provider>
      <resampling maxOversampling='2' zoomedOutResamplingMethod='bilinear' zoomedInResamplingMethod='bilinear' enabled='false'/>
    </provider>
    <rasterrenderer alphaBand='-1' classificationMax='-50' classificationMin='-350' opacity='1' band='1' type='singlebandpseudocolor'>
      <rasterTransparency>
        <singleValuePixelList>
          <pixelListEntry min='-99999' max='-99999' percentTransparent='100'/>
        </singleValuePixelList>
      </rasterTransparency>
      <rastershader>
        <colorrampshader maximumValue='-50' labelPrecision='0' clip='0' colorRampType='DISCRETE' minimumValue='-350'>
          <item alpha='255' value='-340.0' label='< -340 nT (-350 nT)' color='#04b4e6'/>
          <item alpha='255' value='-320.0' label='-340 a -320 nT' color='#5ac4ea'/>
          <item alpha='255' value='-300.0' label='-320 a -300 nT' color='#82cfeb'/>
          <item alpha='255' value='-280.0' label='-300 a -280 nT' color='#a6d7e2'/>
          <item alpha='255' value='-260.0' label='-280 a -260 nT' color='#cbe8dd'/>
          <item alpha='255' value='-240.0' label='-260 a -240 nT' color='#dfefde'/>
          <item alpha='255' value='-220.0' label='-240 a -220 nT' color='#e3f2e7'/>
          <item alpha='255' value='-200.0' label='-220 a -200 nT' color='#f0f7e7'/>
          <item alpha='255' value='-180.0' label='-200 a -180 nT' color='#fffcdf'/>
          <item alpha='255' value='-160.0' label='-180 a -160 nT' color='#fffbd2'/>
          <item alpha='255' value='-140.0' label='-160 a -140 nT' color='#ffeebc'/>
          <item alpha='255' value='-120.0' label='-140 a -120 nT' color='#ffe4b8'/>
          <item alpha='255' value='-100.0' label='-120 a -100 nT' color='#fdd1b0'/>
          <item alpha='255' value='-80.0' label='-100 a -80 nT' color='#faad7c'/>
          <item alpha='255' value='-60.0' label='-80 a -60 nT' color='#f89b5c'/>
          <item alpha='255' value='50.0' label='> -60 nT (-50 nT)' color='#f58345'/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness='0' contrast='0' gamma='1'/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>