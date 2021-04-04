package com.example.demo.Controllers;

import com.example.demo.Entities.Bot_User;
import com.example.demo.Entities.Status;
import com.example.demo.Repositories.Bot_UserRepository;
import com.example.demo.Repositories.StatusRepository;
import org.springframework.data.domain.Example;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
public class Bot_UserController {

    private Bot_UserRepository repository;
    private StatusRepository statusRepository;

    public Bot_UserController(Bot_UserRepository repository, StatusRepository statusRepository) {
        this.repository = repository;
        this.statusRepository = statusRepository;
    }

    @GetMapping("/")
    public HttpStatus greeting(){
        return HttpStatus.OK;
    }

    @GetMapping("/allUsers")
    public List<Bot_User> allUsers(){
        return repository.findAll();
    }
    @GetMapping("/blockedusers")
    public List blockedUsers(){
        Bot_User user = new Bot_User();
        Status status= new Status();
        status.setId(3);
        status.setStatus("Blacklist");
        user.setStatus(status);
        Example<Bot_User> example = Example.of(user);
        List<Bot_User> blockedUser = repository.findAll(example);
        List result = new ArrayList();
        for ( Bot_User indiuser : blockedUser){
            Map<String, String> map = new HashMap<>();
            map.put("id" , indiuser.getId().toString());
            map.put("firstname", indiuser.getFirstname());
            result.add(map);
        }
        return result;
    }
    @GetMapping("/getUser/{id}")
    public boolean getUser(@PathVariable Integer id){
        return repository.existsById(id);
    }

    @PostMapping(
            value ="/addAUser",
            produces = MediaType.APPLICATION_JSON_VALUE)
    public HttpStatus putInWaitingList(@RequestBody Bot_User user){

        Bot_User newUser = new Bot_User();
        repository.save(user);
        return HttpStatus.OK;
    }
    @PutMapping("/chageStatus/{id}")
    public HttpStatus changeStatus(@PathVariable Integer id, @RequestBody Status status){
        System.out.println(id);
        System.out.println(status.getStatus());
        System.out.println(status.getId());
        repository.findById(id)
                .map(Bot_User -> {
                    Bot_User.setStatus(status);
                    //return repository.save();
                    return repository.saveAndFlush(Bot_User);
                });
        return HttpStatus.OK;
    }
}
