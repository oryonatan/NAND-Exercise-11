cd ~/tecs-software-suite-2.5/bin/classes/

echo '====FrogGame.xml====' 
java TextComparer ~/test/hardFiles/FrogGame.xml ~/test/hardFiles/FrogGameA.xml

echo '====GameControl.xml====' 
java TextComparer ~/test/hardFiles/GameControl.xml ~/test/hardFiles/GameControlA.xml
echo '====in3.xml====' 
java TextComparer ~/test/hardFiles/in3.xml ~/test/hardFiles/in3A.xml
echo '====simpleCommentTest.xml====' 
java TextComparer ~/test/hardFiles/simpleCommentTest.xml ~/test/hardFiles/simpleCommentTestA.xml
echo '====Surface.xml====' 
java TextComparer ~/test/hardFiles/Surface.xml ~/test/hardFiles/SurfaceA.xml
echo '====try2.xml===='
java TextComparer ~/test/hardFiles/try2.xml ~/test/hardFiles/try2A.xml
