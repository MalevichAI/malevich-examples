for dir in ./*  
do
    if [[ -f ${dir}/malevich.yaml ]];
    then
        cd ${dir}
        files=$(find ./ -name "*.malevichflow")
        
        malevich space login --username $SPACE_USERNAME --password $SPACE_PASSWORD  --api-url $SPACE_API_URL
        malevich restore  
      for file in $files
      do
        malevich space flow upload $file
      done
      cd ..
    fi
done